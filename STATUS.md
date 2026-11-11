# Reqable Bridge — v0.1 status

- Source archive uploaded to the repository as seven binary segments.
- Archive reconstruction is pinned to SHA-256: `50e8eaff4491a78d71c2371f37ff7f3f2be16a6924b85c68aeef9ae826e824b9`.
- Windows bridge Python syntax check: passed in the initial local check.
- Windows bridge unit/integration tests: 10 passed in the initial local run (Python 3.13); Windows CI also passed 10/10.
- First Android CI build reached Kotlin compilation and identified two Compose import issues; the source assembly script and CI now apply the compatibility fix.
- Android Gradle build: awaiting the corrected CI run.
- OnePlus Ace 6 hotspot reachability: not yet tested.
- Real Reqable Report Server → Android transfer: not yet tested.
- Remote start/pause on the installed Reqable desktop: not yet tested.

No APK or Windows EXE is claimed as built or device-verified yet.
