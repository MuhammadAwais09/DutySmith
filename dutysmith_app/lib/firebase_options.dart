import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) return web;

    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;

      // You have not provided iOS config for dutysmith-25ccb yet.
      // Add an iOS app in Firebase Console and then fill FirebaseOptions for iOS.
      case TargetPlatform.iOS:
        throw UnsupportedError(
          'iOS is not configured. Add iOS app in Firebase and update firebase_options.dart',
        );

      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyDdRS9eN2K6Hq39RS6eoYnyUWqkjseQwzY',
    appId: '1:761416400146:android:d3bbaa372d30d6f83487cb',
    messagingSenderId: '761416400146',
    projectId: 'dutysmith-25ccb',
    databaseURL: 'https://dutysmith-25ccb-default-rtdb.firebaseio.com',
    storageBucket: 'dutysmith-25ccb.firebasestorage.app',
  );

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyD07dh8aaxBoMVaYzinm3BaUe4CC1z1VjA',
    appId: '1:761416400146:web:a89e65a3a92df1dd3487cb',
    messagingSenderId: '761416400146',
    projectId: 'dutysmith-25ccb',
    authDomain: 'dutysmith-25ccb.firebaseapp.com',
    databaseURL: 'https://dutysmith-25ccb-default-rtdb.firebaseio.com',
    storageBucket: 'dutysmith-25ccb.firebasestorage.app',
    measurementId: 'G-162GLLHX30',
  );
}