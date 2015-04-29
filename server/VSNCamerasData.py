__author__ = 'Amin'

from common.VSNPacket import IMAGE_TYPES
from client.VSNActivityController import GainSampletimeTuple

import pickle


class VSNCameraData:
    def __init__(self):
        # data from camera
        self.activation_level = 0.0
        self._activation_level_history = []
        self.percentage_of_active_pixels = 0.0
        self._percentage_of_active_pixels_history = []
        # data to camera that is calculated periodically
        self.activation_neighbours = 0.0                           # weighted activity of neighbouring nodes
        # internal counters of camera state
        self.ticks_in_low_power_mode = 0
        self.ticks_in_normal_operation_mode = 0
        # camera parameters
        self.flag_send_image = False
        self.image_type = IMAGE_TYPES.foreground
        self._parameters_below_threshold = GainSampletimeTuple(2.0, 1.0)
        self._parameters_above_threshold = GainSampletimeTuple(0.1, 0.1)
        self._activation_level_threshold = 10.0
        self._parameters = self._parameters_below_threshold         # sample time and gain at startup
        # flag indicating that parameters should be send to camera
        self.flag_parameters_changed = True

    def update(self, activation_level, percentage_of_active_pixels):
        self.activation_level = activation_level
        self.percentage_of_active_pixels = percentage_of_active_pixels

        self._activation_level_history.append(activation_level)
        self._percentage_of_active_pixels_history.append(percentage_of_active_pixels)

        self._update_ticks_counters()

    def _update_ticks_counters(self):
        if self.activation_level < self._activation_level_threshold:
            self.ticks_in_low_power_mode += 10
        else:
            self.ticks_in_normal_operation_mode += 1




class VSNCameras:
    def __init__(self):
        # TODO: this should be automatically created or even put inside the CameraData class
        self._dependency_table = {
            'picam01': [0.0, 0.7, 0.3, 0.0, 0.0],
            'picam02': [0.5, 0.0, 0.5, 0.2, 0.0],
            'picam03': [0.2, 0.5, 0.0, 0.5, 0.2],
            'picam04': [0.0, 0.2, 0.5, 0.0, 0.5],
            'picam05': [0.0, 0.0, 0.3, 0.7, 0.0]
        }

        self.cameras = {}
        # TODO: remove the automatic creation of 4 cameras and do it as new cameras connect
        self.add_camera(1)
        self.add_camera(2)
        self.add_camera(3)
        self.add_camera(4)
        self.add_camera(5)

    def choose_camera_to_stream(self, camera_name):
        for key in self.cameras:
            self.cameras[key].flag_send_image = False
        self.cameras[str(camera_name)].flag_send_image = True

    def get_flag_send_image(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].flag_send_image

    def get_activation_neighbours(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].activation_neighbours

    def get_percentage_of_active_pixels(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].percentage_of_active_pixels

    def get_status(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        return (camera_name,
                self.cameras[camera_name].percentage_of_active_pixels,
                self.cameras[camera_name].activation_level,
                self.cameras[camera_name].activation_neighbours,
                self.cameras[camera_name]._parameters.gain,
                self.cameras[camera_name]._parameters.sample_time,
                self.cameras[camera_name].ticks_in_low_power_mode,
                self.cameras[camera_name].ticks_in_normal_operation_mode
                )

    def add_camera(self, camera_number):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)
        self.cameras[camera_name] = VSNCameraData()

    def _convert_camera_number_to_camera_name(self, camera_number):
        camera_name = "picam" + str(camera_number).zfill(2)
        return camera_name

    def save_cameras_data_to_files(self):
        for i in xrange(1, 6):
            camera_name = self._convert_camera_number_to_camera_name(i)
            new_file = file(camera_name + ".txt", "w")

            pickle.dump(self.cameras[camera_name], new_file)

            new_file.close()

    def update_state(self, camera_number, activation_level, percentage_of_active_pixels):
        camera_name = self._convert_camera_number_to_camera_name(camera_number)

        self.cameras[camera_name].update(activation_level, percentage_of_active_pixels)

        return self._calculate_neighbour_activation_level(camera_name)

    def _calculate_neighbour_activation_level(self, camera_name):
        # TODO: change it to check against the real number of cameras in the system
        self.cameras[camera_name].activation_neighbours = 0.0
        for idx in xrange(0, len(self.cameras)-1):
            # idx+1 is used because cameras are numbered 1, 2, 3, 4, 5
            current_camera_name = "picam" + str(idx+1).zfill(2)
            self.cameras[camera_name].activation_neighbours += \
                self._dependency_table[camera_name][idx] * self.cameras[current_camera_name].percentage_of_active_pixels

        return self.cameras[camera_name].activation_neighbours

        #self._activation_neighbours[node_index] = 0
        #for idx in xrange(0, 3):
        #    self._activation_neighbours[node_index] += \
        #        dependency_table[node_name][idx] * self._graphsController._percentages[idx]