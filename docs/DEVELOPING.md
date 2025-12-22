# Developing

This document has some info on how to develop for this package.

## Dev environment

The package has no specific build/package tool requirements other than a standard virtual env. It should work with any editor, but I only used it with VS Code.

These are the commands to setup a dev environment and run the tests after the repo has been cloned.

```bash
# Create a virtual env
$python3.13 -m venv venv
# Activate the virtual env
$source ./venv/bin/activate
# Install package as editable with dev dependencies
$pip install -e .[dev]
# Run all tests with coverage and run mypy
$./coverage.sh
```

## CI

CI is a bit barebones, but it does:

* Run mypy
* Run tests
* When pushing a version tag a sanity check is done against the version number in `pyproject.toml` to make sure they match
* When a release is made it gets automatically uploaded to PyPi.

For details see the task files under `.github/workflows`

## Releasing

Releasing is not difficult, but could be a bit more automated.

* Do any tests you want to do before release
* Run `bump_version` script with the new version and follow the prompts. When done a version tag has been created and pushed to Github
* Wait a bit until [the actions](https://github.com/mvdwetering/ynca/actions) are all done without errors
* [On Github](https://github.com/mvdwetering/ynca/tags) create a release from the tag that was pushed
* Write the release notes and save
* The package will be automatically uploaded to PyPi

## Adding Commands

This section is a crash course on how to add new YNCA commands to the package.

In general just look at similar existing commands for inspiration.

But basically the steps would be:

* Figure out the command name and the values it accepts. This can be done by changing the setting on the receiver and see what commands are coming out. Usually it is pretty straight forward to see what you need to send.
* Find the file for subunit to add the command to in `src/ynca/subunits`
* Add an attribute with a suitable `FunctionMixin` from `src/ynca/function.py`
  * If needed add an enum to `src/ynca/enums.py` and export the type from the `__init__.py`
* Add a test
* Done

### Example

As an example lets take a look at the Extra Bass setting.

#### Figure out the commands

The command to use is `@MAIN:EXBASS=Auto` to turn it on and `@MAIN:EXBASS=Off` to turn it off. This was obtained from a user that submitted the diagnostics from the `yamaha_ynca` integration. See <https://github.com/mvdwetering/yamaha_ynca/issues/478>

#### Find the file for the subunit

This setting probably only applies to the MAIN zone, but I put it in the ZoneBase so all zones will have it just in case. Maybe this is overkill.

The file for ZoneBase is `src/ynca/subunits/zone.py`

#### Add attribute to the Subunit subclass

I this case added an `EnumFunctionMixin` because the value is an enum. I use enums instead of booleans because on multiple occasions it turned out that different models would have additional or different values. With an enum it is easy to add, with a bool you are stuck.

This does mean a new `Enum` has to be added to `src/ynca/enums.py`. The `__missing__` dunder method is to  trigger a warning on unknown values.

```python
@unique
class ExtraBass(StrEnum):
    AUTO = "Auto"
    OFF = "Off"

    @classmethod
    def _missing_(cls, value: object) -> Self:
        logger.warning("Unknown value '%s' in %s", value, cls.__name__)
        return cls(cls.UNKNOWN)

    UNKNOWN = UNKNOWN_STRING
    """Unknown values in the enum are mapped to UNKNOWN"""
```

Now the new type should be exported from the package. This is done in `src/ynca/__init__.py` look at others for inspiration. Be aware that the type needs to be imported into the `__init__.py` and added to the `__all__` list.

Now use the type with the `EnumFunctionMixin` (because it is an Enum, there are also FunctionMixins for strings, ints and more). The `EnumFunctionMixin` is a Python descriptor which, in combination with the subunit it is part of, will take care of sending a command when a value is assigned to `exbass` and will make it so that when reading the `exbass` attribute the latest received value will be returned.

Note that the attribute name should match the YNCA commandname. If that is not possible it can be overridden with `name_override`, see 2CHDECODER for an example. Also checkout the documentation on the `FunctionMixinBase` which describes the `name_override` and other options.

Please keep the commands/enums alphabetically ordered.

```python
class ZoneBase(PlaybackFunctionMixin, SubunitBase):
    ... lots more ...
    exbass = EnumFunctionMixin[ExtraBass](ExtraBass)
```

#### Add a test

When running the `coverage.sh` script you will notice there is some missing coverage. I keep it at 100% so it is easy to see what still needs work. Note that 100% coverage does not neccesarily means it is really tested, just that the line is hit at some point.

In this case check out `test_enums.py` and add a line that checks the UNKNOWN value.
And in `test_zone.py` add a test for the sending/receiving of the command.

#### Done

You are now an expert.

Other commands are similar, check out existing commands for reference.
There is also the git history which might have relevant commits to whatever you are trying to do.
