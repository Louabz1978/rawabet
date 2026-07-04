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

## Production Signing

Android will not treat a debug APK like a trusted company app. The release build must be signed with your private production key.

Create the private key once and keep it safe:

```bash
mkdir -p ~/rawabet-android-keys
keytool -genkeypair \
  -v \
  -keystore ~/rawabet-android-keys/rawabet-release.jks \
  -alias rawabet \
  -keyalg RSA \
  -keysize 4096 \
  -validity 10000
```

Before building, export the signing values in the same terminal:

```bash
export RAWABET_KEYSTORE_PATH="$HOME/rawabet-android-keys/rawabet-release.jks"
export RAWABET_KEY_ALIAS="rawabet"
export RAWABET_KEYSTORE_PASSWORD="YOUR_KEYSTORE_PASSWORD"
export RAWABET_KEY_PASSWORD="YOUR_KEY_PASSWORD"
```

Do not commit the `.jks` file or passwords.

## Build Release APK

From the project root:

```bash
npm install --prefix frontend
npm run android:sync --prefix frontend
cd frontend/android
./gradlew clean assembleRelease
```

The signed release APK will be created at:

```text
frontend/android/app/build/outputs/apk/release/app-release.apk
```

Rename it for distribution:

```bash
cp app/build/outputs/apk/release/app-release.apk ../../dist-apk/rawabet_v1.1.0.apk
```

## Build Play Store / Managed Store Bundle

For the Google Play Store or a managed enterprise store, build an Android App Bundle:

```bash
cd frontend/android
./gradlew clean bundleRelease
```

The signed bundle will be created at:

```text
frontend/android/app/build/outputs/bundle/release/app-release.aab
```

## Important Android Warning Notes

- A signed release APK removes the debug/test-app warning.
- If users download the APK directly from your website, Android may still show an "unknown app/source" warning because the app is not installed from Google Play or a trusted managed store.
- To make installs feel like other company apps, publish through Google Play, Google Play private/closed testing, Managed Google Play, Samsung Galaxy Store, or an MDM/enterprise app catalog.
- Host direct APK downloads only over HTTPS and keep the package name and signing key unchanged for future updates.

## Update App After Frontend Changes

```bash
npm run android:sync --prefix frontend
```

Then rebuild the signed release APK or AAB.
