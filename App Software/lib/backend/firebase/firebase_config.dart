import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';

Future initFirebase() async {
  if (kIsWeb) {
    await Firebase.initializeApp(
        options: FirebaseOptions(
            apiKey: "AIzaSyAfjauQCAf7Na-iPwNSaTLgKTw2zuYP3rI",
            authDomain: "smartbell-372ba.firebaseapp.com",
            projectId: "smartbell-372ba",
            storageBucket: "smartbell-372ba.appspot.com",
            messagingSenderId: "235504085161",
            appId: "1:235504085161:web:26f283074479263f9ae1b8",
            measurementId: "G-DLQ973YTLY"));
  } else {
    await Firebase.initializeApp();
  }
}
