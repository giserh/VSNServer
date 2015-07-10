import pickle

from server.VSNCamera import VSNCamera


class VSNCameras:
    def __init__(self):
        # TODO: this should be automatically created or even put inside the CameraData class
        self.__dependency_table = {
            'picam01': [0.0, 0.5, 0.2, 0.0, 0.0],
            'picam02': [0.5, 0.0, 0.5, 0.1, 0.0],
            'picam03': [0.1, 0.5, 0.0, 0.5, 0.2],
            'picam04': [0.0, 0.1, 0.5, 0.0, 0.5],
            'picam05': [0.0, 0.0, 0.2, 0.5, 0.0]
        }

        self.cameras = {}

    @staticmethod
    def __convert_camera_number_to_camera_name(camera_number):
        camera_name = "picam" + str(camera_number).zfill(2)
        return camera_name

    def __calculate_neighbour_activation_level(self, camera_name):
        # TODO: change it to check against the real number of cameras in the system
        self.cameras[camera_name].activation_neighbours = 0.0
        for idx in range(0, len(self.cameras) - 1):
            # idx+1 is used because cameras are numbered 1, 2, 3, 4, 5
            current_camera_name = 'picam' + str(idx + 1).zfill(2)
            self.cameras[camera_name].activation_neighbours += \
                self.__dependency_table[camera_name][idx] * self.cameras[current_camera_name].percentage_of_active_pixels

        return self.cameras[camera_name].activation_neighbours

    def choose_camera_to_stream(self, camera_name):
        for key in self.cameras:
            self.cameras[key].stop_sending_image()
        self.cameras[str(camera_name)].start_sending_image()

    def get_activation_neighbours(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].activation_neighbours

    def get_percentage_of_active_pixels(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return self.cameras[camera_name].percentage_of_active_pixels

    def get_status(self, camera_number):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)
        return (camera_name,
                self.cameras[camera_name].percentage_of_active_pixels,
                self.cameras[camera_name].activation_level,
                self.cameras[camera_name].activation_neighbours,
                self.cameras[camera_name].parameters.gain,
                self.cameras[camera_name].parameters.sample_time,
                self.cameras[camera_name].ticks_in_low_power_mode,
                self.cameras[camera_name].ticks_in_normal_operation_mode
                )

    def set_image_type(self, camera_name, image_type):
        self.cameras[camera_name].change_image_type(image_type)

    def add_camera(self, client):
        camera_name = self.__convert_camera_number_to_camera_name(client.id)
        self.cameras[camera_name] = VSNCamera(client)

    def save_cameras_data_to_files(self):
        for i in range(1, 6):
            camera_name = self.__convert_camera_number_to_camera_name(i)
            with open(camera_name + ".txt", "wb") as file:
                pickle.dump(self.cameras[camera_name], file)

    def load_cameras_data_from_files(self):
        for i in range(1, 6):
            camera_name = self.__convert_camera_number_to_camera_name(i)
            with(camera_name + ".txt", "rb") as file:
                self.cameras[camera_name] = pickle.load(file)

    def clear_cameras_data(self):
        for i in range(1, 6):
            camera_name = self.__convert_camera_number_to_camera_name(i)
            self.cameras[camera_name].clear_history()

    def update_state(self, camera_number, activation_level, percentage_of_active_pixels):
        camera_name = self.__convert_camera_number_to_camera_name(camera_number)

        self.cameras[camera_name].update(activation_level, percentage_of_active_pixels)

        return self.__calculate_neighbour_activation_level(camera_name)

        # self._activation_neighbours[node_index] = 0
        # for idx in range(0, 3):
        #    self._activation_neighbours[node_index] += \
        #        dependency_table[node_name][idx] * self._graphsController._percentages[idx]
