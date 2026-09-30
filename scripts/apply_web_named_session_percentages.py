from pathlib import Path

root = Path('.')

report = root / "lib/services/report_service.dart"
text = report.read_text(encoding="utf-8")

if "class CourseAttendanceSummary" not in text:
    marker = "class ReportService {"
    course_class = """class CourseAttendanceSummary {
  const CourseAttendanceSummary({
    required this.courseName,
    required this.attended,
    required this.totalSessions,
  });

  final String courseName;
  final int attended;
  final int totalSessions;

  double get percentage =>
      totalSessions == 0 ? 0 : attended * 100 / totalSessions;
}

"""
    if marker not in text:
        raise SystemExit("ReportService class marker not found")
    text = text.replace(marker, course_class + marker, 1)

if "List<CourseAttendanceSummary> summarizeByCourse" not in text:
    marker = "  AttendanceSummary summarize(List<AttendanceRecord> records) {"
    method = """  List<CourseAttendanceSummary> summarizeByCourse(
    List<AttendanceRecord> records,
  ) {
    final groups = <String, List<AttendanceRecord>>{};
    for (final record in records) {
      final displayName = record.sessionTitle.trim().isEmpty
          ? 'Attendance session'
          : record.sessionTitle.trim();
      final key = displayName.toLowerCase();
      groups.putIfAbsent(key, () => []).add(record);
    }

    final summaries = groups.entries.map((entry) {
      final courseRecords = entry.value;
      final displayName = courseRecords.first.sessionTitle.trim().isEmpty
          ? 'Attendance session'
          : courseRecords.first.sessionTitle.trim();
      final attended =
          courseRecords.where((record) => record.isPresent).length;
      return CourseAttendanceSummary(
        courseName: displayName,
        attended: attended,
        totalSessions: courseRecords.length,
      );
    }).toList();

    summaries.sort(
      (a, b) => a.courseName.toLowerCase().compareTo(
        b.courseName.toLowerCase(),
      ),
    );
    return summaries;
  }

"""
    if marker not in text:
        raise SystemExit("ReportService summarize marker not found")
    text = text.replace(marker, method + marker, 1)

report.write_text(text, encoding="utf-8")

student = root / "lib/screens/student_dashboard.dart"
text = student.read_text(encoding="utf-8")

old_rate = """                Expanded(
                  child: SummaryCard(
                    label: 'Rate',
                    value: '${summary.percentage.toStringAsFixed(0)}%',
                    icon: Icons.percent,
                    color: Theme.of(context).colorScheme.secondary,
                  ),
                ),"""
new_rate = """                Expanded(
                  child: SummaryCard(
                    label: 'Sessions',
                    value: '${summary.sessions}',
                    icon: Icons.event_note_outlined,
                    color: Theme.of(context).colorScheme.secondary,
                  ),
                ),"""
if old_rate not in text:
    raise SystemExit("Student dashboard global Rate card not found")
text = text.replace(old_rate, new_rate, 1)

anchor = """            const SizedBox(height: 22),
            FilledButton.icon(
              onPressed: () => Navigator.push("""
course_block = """            const SizedBox(height: 22),
            Text(
              'Attendance by course',
              style: Theme.of(context).textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 9),
            if (ReportService.instance.summarizeByCourse(records).isEmpty)
              const Card(
                child: ListTile(
                  leading: Icon(Icons.school_outlined),
                  title: Text('No completed sessions yet'),
                ),
              )
            else
              ...ReportService.instance.summarizeByCourse(records).map(
                (course) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Card(
                    child: ListTile(
                      leading: const Icon(Icons.school_outlined),
                      title: Text(
                        course.courseName,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                      subtitle: Text(
                        '${course.attended} attended / ${course.totalSessions} sessions',
                      ),
                      trailing: Text(
                        '${course.percentage.toStringAsFixed(2)}%',
                        style: const TextStyle(fontWeight: FontWeight.w900),
                      ),
                    ),
                  ),
                ),
              ),
            const SizedBox(height: 22),
            FilledButton.icon(
              onPressed: () => Navigator.push("""
if anchor not in text:
    raise SystemExit("Student dashboard insertion anchor not found")
text = text.replace(anchor, course_block, 1)
student.write_text(text, encoding="utf-8")

admin = root / "lib/screens/admin_reports_page.dart"
text = admin.read_text(encoding="utf-8")

old_group = """      final groups = <String, List<AttendanceRecord>>{};
      for (final record in records) {
        groups.putIfAbsent(record.studentUid, () => []).add(record);
      }
      final studentSummaries = groups.values.toList()
        ..sort((a, b) => a.first.studentName.compareTo(b.first.studentName));"""
new_group = """      final groups = <String, List<AttendanceRecord>>{};
      for (final record in records) {
        final courseKey = record.sessionTitle.trim().toLowerCase();
        final key = '${record.studentUid}::$courseKey';
        groups.putIfAbsent(key, () => []).add(record);
      }
      final studentSummaries = groups.values.toList()
        ..sort((a, b) {
          final studentCompare =
              a.first.studentName.compareTo(b.first.studentName);
          if (studentCompare != 0) return studentCompare;
          return a.first.sessionTitle.toLowerCase().compareTo(
            b.first.sessionTitle.toLowerCase(),
          );
        });"""
if old_group not in text:
    raise SystemExit("Admin report student grouping block not found")
text = text.replace(old_group, new_group, 1)

old_row = """                    title: Text(
                      studentRecords.first.studentName,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    subtitle: Text(
                      '${studentRecords.first.studentNumber} • ${studentSummary.present}/${studentSummary.totalRecords} present',
                    ),"""
new_row = """                    title: Text(
                      '${studentRecords.first.studentName} • ${studentRecords.first.sessionTitle}',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    subtitle: Text(
                      '${studentRecords.first.studentNumber} • ${studentSummary.present}/${studentSummary.totalRecords} present',
                    ),"""
if old_row not in text:
    raise SystemExit("Admin report student summary row not found")
text = text.replace(old_row, new_row, 1)
admin.write_text(text, encoding="utf-8")

service = (root / "lib/services/attendance_service.dart").read_text(encoding="utf-8")
if ".collection('sessions').doc();" not in service:
    raise SystemExit("Unique session-instance creation was not found; refusing to continue")

for path, needles in {
    report: ["class CourseAttendanceSummary", "summarizeByCourse"],
    student: ["Attendance by course", "course.percentage.toStringAsFixed(2)"],
    admin: ["record.sessionTitle.trim().toLowerCase()", "studentRecords.first.sessionTitle"],
}.items():
    current = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in current:
            raise SystemExit(f"Named-session verification failed: {needle}")

print("Named-session attendance percentage update verified.")
