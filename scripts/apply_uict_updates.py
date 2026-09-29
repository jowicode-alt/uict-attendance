        if lines[j].lstrip().startswith('if ') or lines[j].lstrip().startswith('if('):
            start = j
            break
    brace_line = next((j for j in range(start, len(lines)) if '{' in lines[j]), None)
    if brace_line is not None:
        depth = 0
        end = brace_line
        for j in range(brace_line, len(lines)):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth == 0:
                end = j
                break
        del lines[start:end + 1]
    else:
        del lines[idx]
lines = [line for line in lines if '_networkInfo' not in line and 'network_info_plus' not in line]
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