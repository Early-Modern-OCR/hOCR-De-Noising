import json


# REF: http://www.yilmazhuseyin.com/blog/dev/advanced_json_manipulation_with_python/
class EmopEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return str(type(obj))


class EmopStdlib(object):

    @staticmethod
    def to_JSON(obj):
        return json.dumps(obj, sort_keys=True, indent=4, cls=EmopEncoder)
