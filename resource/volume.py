from resource.header import ResourceHeader


class VolumeReader:
    def __init__(self, path):
        self.vol_file = open(path, 'rb')

    def read_resource(self, offset):
        header = ResourceHeader.parse(self.vol_file, offset)
        return header, self.vol_file.read(header.length)

    def close(self):
        self.vol_file.close()
