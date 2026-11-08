from resource.objects import Object, decrypt_object_file


def inventory(game):
    return Object.extract_inventory_objects(game.path / "OBJECT")


class TestObjects:
    def test_names(self, game):
        names = [bytes(o.name) for o in inventory(game)]
        assert names == [n.encode("ascii") for n in game.objects["names"]]

    def test_rooms(self, game):
        assert [o.room for o in inventory(game)] == game.objects["rooms"]

    def test_indices_are_sequential(self, game):
        assert [o.index for o in inventory(game)] == list(range(len(game.objects["names"])))

    def test_max_animated(self, game):
        max_animated, _ = Object.extract_object_header_data(decrypt_object_file(game.path / "OBJECT"))
        assert max_animated == game.objects["max_animated"]
