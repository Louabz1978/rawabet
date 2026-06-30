# Rawabet Android APK

The Android app is built from the existing Rawabet frontend using Capacitor.
It connects to the production API:

```text
https://rawabet-sy.com/api
```

## Requirements

- Java JDK 17
- Android Studio or Android command-line tools
- Android SDK Platform installed
- Android SDK Build Tools installed

## Build

From the project root:

```bash
npm install --prefix frontend
npm run android:sync --prefix frontend
cd frontend/android
./gradlew assembleDebug
```

The debug APK will be created at:

```text
frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

For a production APK, create a signing key and run a signed release build from Android Studio.

## Update App After Frontend Changes

```bash
npm run android:sync --prefix frontend
```

Then rebuild the APK.
