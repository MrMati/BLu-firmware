class Nothing:
    def __call__(self, *args, **kwargs):
        return Nothing()

    def __cmp__(self, other):
        if other.__class__ == Nothing:
            return 0

        return -1

    def __getattr__(self, name):
        return Nothing()

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return Nothing()

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __repr__(self):
        return 'None'

    def __str__(self):
        return 'None'

    def __nonzero__(self):
        return False


def maybe(val):
    if val is None:
        return Nothing()
    return val
