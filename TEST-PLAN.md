- As the project is in mid-development, most tests up to date have been in-progress verification tests. These remain in source control and will be brought back when it is time to establish a battery of formal tests.
- A number of the parts I intend to test are being reworked, so establishing a battery of unit/regression tests is being put off a little bit in order to focus on the program. However, as of May 28 (2021) I have placed every method in its own file in preparation of establishing these tests.
- Part of the purpose of establishing these tests is to set a standard for third-party contributors - I cannot ask them to do what I will not.
- I have done some research and have decided that I am most comfortable with Python's unittest functionality to create and run most tests.
- All public methods and functions get tested, eventually.
- I will introduce mutation tests to validate the tests themselves. This implies we need some form of runtime selecion in order to hit-up the most recently-modified ones first.
- The most important tests are the validation tests; these will likely come even before most unit tests.
