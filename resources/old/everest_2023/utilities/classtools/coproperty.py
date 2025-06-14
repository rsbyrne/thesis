###############################################################################
''''''
###############################################################################


class CoProperty(property):

    def __set_name__(self, owner, name):
        self.cooperators = tuple(  # pylint: disable=W0201
            acls.__dict__[name] for acls in owner.__bases__
                if name in acls.__dict__
            )

    def allyield(self, instance, owner):
        for coop in self.cooperators:
            yield from coop.allyield(instance, owner)
        yield from super().__get__(instance, owner)

    def __get__(self, instance, owner):
        return tuple(self.allyield(instance, owner))


coproperty = CoProperty.__call__


###############################################################################
###############################################################################
