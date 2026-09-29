from pathlib import Path
import re, json

import os

root = Path(os.environ.get('PROJECT_ROOT', '.'))

for p in (root/'lib').rglob('*.dart'):
    s = p.read_text()
    for a,b in [
        ('WIZZARD NATION','DIGITAL DYNAMOS'),
        ('Wizzard Nation','Digital Dynamos'),
        ('wizzard nation','digital dynamos'),
        ('Administrator','Lecturer'),
        ('administrator','lecturer'),
        ('ADMINISTRATOR','LECTURER'),
        ('an lecturer','a lecturer'),
    ]:
        s = s.replace(a,b)
    p.write_text(s)

p=root/'lib/models/attendance_models.dart'; s=p.read_text()
s=s.replace('    required this.allowedWifiSsids,\n','')
s=s.replace('  final List<String> allowedWifiSsids;\n','')
s=re.sub(r'  bool get isConfigured =>.*?;\n', '  bool get isConfigured => campusLocation != null && radiusMeters > 0;\n', s, count=1, flags=re.S)
s=re.sub(r'      allowedWifiSsids: List<String>.from\(.*?\n      \),\n', '', s, count=1, flags=re.S)
p.write_text(s)

p=root/'lib/services/attendance_service.dart'; s=p.read_text()
s=s.replace("import 'package:network_info_plus/network_info_plus.dart';\n",'')
s=s.replace('  final NetworkInfo _networkInfo = NetworkInfo();\n','')
s=s.replace('    required List<String> wifiSsids,\n','')
s=re.sub(r'    final cleaned = wifiSsids.*?\n    await _db\.collection\(\'settings\'\)\.doc\(\'attendance\'\)\.set\(\{\n      \'allowedWifiSsids\': cleaned,\n', "    await _db.collection('settings').doc('attendance').set({\n", s, count=1, flags=re.S)
s=s.replace('Configure classroom Wi-Fi and GPS settings before opening attendance.','Configure the attendance location settings before opening attendance.')
s=re.sub(r'    // Android and iOS expose the Wi-Fi name.*?\n\n    final position = await currentPosition\(\);\n', '    final position = await currentPosition();\n', s, count=1, flags=re.S)
s=s.replace("      'wifiSsid': wifiName,\n",'')
s=s.replace('administratorsStream()', 'lecturersStream()')
s=s.replace("        ?.replaceAll('\"', '')\n        .trim();\n", '')

# Remove the legacy Wi-Fi validation block without touching unrelated service methods.
lines = s.splitlines()
while True:
    hit = next((i for i, line in enumerate(lines) if 'allowedWifiSsids' in line), None)
    if hit is None:
        break
    start = hit
    for j in range(hit - 1, max(-1, hit - 20), -1):
        if lines[j].lstrip().startswith('if ') or lines[j].lstrip().startswith('if('):
            start = j
            break
    depth = 0
    end = hit
    found_brace = False
    for j in range(start, len(lines)):
        depth += lines[j].count('{') - lines[j].count('}')
        if '{' in lines[j]:
            found_brace = True
        if found_brace and depth == 0:
            end = j
            break
    del lines[start:end + 1]
lines = [line for line in lines if '_networkInfo' not in line and 'network_info_plus' not in line and 'wifiName' not in line]
s = '\n'.join(lines) + '\n'
p.write_text(s)

p=root/'lib/screens/admin_settings_page.dart'; s=p.read_text()
s=s.replace('  final _wifi = TextEditingController();\n','')
s=s.replace("    _wifi.text = settings.allowedWifiSsids.join(', ');\n",'')
s=s.replace('    _wifi.dispose();\n','')
s=s.replace("if (_wifi.text.trim().isEmpty || latitude == null || longitude == null)", "if (latitude == null || longitude == null)")
s=s.replace("'Enter Wi-Fi names and capture or enter valid campus coordinates.'", "'Capture or enter valid campus coordinates.'")
s=s.replace('        wifiSsids: _wifi.text.split(\',\'),\n','')
s=re.sub(r'                TextField\(\n                  controller: _wifi,.*?                const SizedBox\(height: 14\),\n', '', s, count=1, flags=re.S)
s=s.replace('Students must match both an approved Wi-Fi name and the GPS radius below. Wi-Fi names are case-sensitive.',
            'Students must be inside the approved GPS attendance area below and use the live session QR or code.')
s=s.replace('Use This Phone’s Current Location','Use This Device’s Current Location')
p.write_text(s)

p=root/'lib/screens/student_dashboard.dart'; s=p.read_text()
s=s.replace("""                    const RequirementRow(
                      icon: Icons.wifi,
                      text: 'Connect to the approved classroom Wi-Fi',
                    ),
""",'')
marker="""            const SizedBox(height: 22),
            FilledButton.icon(
"""
block="""            if (records.isNotEmpty) ...[
              const SizedBox(height: 22),
              Text(
                'Attendance by Session',
                style: Theme.of(context).textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 10),
              ..._sessionSummaries(records).entries.map((entry) {
                final present = entry.value.where((r) => r.isPresent).length;
                final total = entry.value.length;
                final rate = total == 0 ? 0.0 : present * 100 / total;
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Card(
                    child: ListTile(
                      leading: const Icon(Icons.event_available_outlined),
                      title: Text(entry.key, style: const TextStyle(fontWeight: FontWeight.w700)),
                      subtitle: Text(present.toString() + ' of ' + total.toString() + ' sessions attended'),
                      trailing: Text(rate.toStringAsFixed(0) + '%', style: const TextStyle(fontWeight: FontWeight.w900)),
                    ),
                  ),
                );
              }),
            ],
            const SizedBox(height: 22),
            FilledButton.icon(
"""
if marker not in s: raise SystemExit('student marker missing')
s=s.replace(marker,block,1)
helper="""Map<String, List<AttendanceRecord>> _sessionSummaries(
  List<AttendanceRecord> records,
) {
  final grouped = <String, List<AttendanceRecord>>{};
  for (final record in records) {
    grouped.putIfAbsent(record.sessionTitle, () => []).add(record);
  }
  return grouped;
}

"""
s=s.replace('class SummaryCard extends StatelessWidget {', helper+'class SummaryCard extends StatelessWidget {',1)
p.write_text(s)

p=root/'pubspec.yaml'; s=p.read_text().replace('version: 1.0.0+1','version: 1.0.1+2').replace('  network_info_plus: ^8.2.1\n',''); p.write_text(s)

p=root/'android/app/src/main/AndroidManifest.xml'; s=p.read_text()
s=s.replace('    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />\n','')
s=s.replace('    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n','')
p.write_text(s)

p=root/'firestore.rules'; s=p.read_text()
s=s.replace("        && request.resource.data.wifiSsid in settings.allowedWifiSsids\n",'')
s=s.replace("'deviceId', 'wifiSsid', 'location', 'accuracyMeters', 'checkedAt'", "'deviceId', 'location', 'accuracyMeters', 'checkedAt'")
p.write_text(s)

p=root/'lib/main.dart'; s=p.read_text()
if "firebase_options.dart" not in s:
    s=s.replace("import 'app.dart';","import 'app.dart';\nimport 'firebase_options.dart';")
s=s.replace('await Firebase.initializeApp();','await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);')
p.write_text(s)

(root/'lib/firebase_options.dart').write_text("""import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) return web;
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      default:
        return android;
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyDOXht78tQrPF1m5gpmjYV-nm0e-OfFAdY',
    appId: '1:1046712358957:android:d0d86dabadbfc952e040a4',
    messagingSenderId: '1046712358957',
    projectId: 'attendence-uict-bbit',
    storageBucket: 'attendence-uict-bbit.firebasestorage.app',
    authDomain: 'attendence-uict-bbit.firebaseapp.com',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyDOXht78tQrPF1m5gpmjYV-nm0e-OfFAdY',
    appId: '1:1046712358957:android:d0d86dabadbfc952e040a4',
    messagingSenderId: '1046712358957',
    projectId: 'attendence-uict-bbit',
    storageBucket: 'attendence-uict-bbit.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyDOXht78tQrPF1m5gpmjYV-nm0e-OfFAdY',
    appId: '1:1046712358957:android:d0d86dabadbfc952e040a4',
    messagingSenderId: '1046712358957',
    projectId: 'attendence-uict-bbit',
    storageBucket: 'attendence-uict-bbit.firebasestorage.app',
  );
}
""")

(root/'web').mkdir(exist_ok=True)
(root/'web/index.html').write_text("""<!DOCTYPE html>
<html><head><base href="\$FLUTTER_BASE_HREF"><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0B1F3A"><title>UICT ATTENDANCE</title>
</head><body><script src="flutter_bootstrap.js" async></script></body></html>
""")
(root/'web/manifest.json').write_text("""{
  "name":"UICT ATTENDANCE","short_name":"UICT ATTENDANCE","start_url":".",
  "display":"standalone","background_color":"#F4F6FA","theme_color":"#0B1F3A",
  "description":"UICT ATTENDANCE"
}
""")
fp=root/'firebase.json'; cfg=json.loads(fp.read_text()); cfg['hosting']={"public":"build/web","ignore":["firebase.json","**/.*","**/node_modules/**"]}; fp.write_text(json.dumps(cfg,indent=2)+"\n")