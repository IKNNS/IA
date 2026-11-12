# Local Codex Worker

โปรเจกต์ตั้งต้นสำหรับให้เครื่องของเรารับงานจากไฟล์ แล้วส่งงานให้ Codex CLI ทำใน local repository

## แนวคิด

```text
jobs/inbox/*.md
        ↓
local worker
        ↓
codex exec
        ↓
runs/<job-id>/
```

โปรเจกต์นี้ไม่ใช้ OpenAI API key และไม่ใช้ Codex Cloud โดยอาศัย Codex CLI ที่ล็อกอินด้วยบัญชี ChatGPT บนเครื่องนี้แทน

## เริ่มต้น

ต้องมี Python 3.11+ และติดตั้ง/ล็อกอิน Codex CLI เรียบร้อยแล้ว

ก่อนรันจริง โปรเจกต์ต้องเป็น Git repository:

```bash
git init
git add .
git commit -m "Initial local Codex worker"
```

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m codex_worker --dry-run
```

คำสั่งด้านบนเป็นการตรวจงานโดยยังไม่เรียก Codex จริง

เมื่อพร้อมให้รันจริง:

```bash
python -m codex_worker --execute
```

ค่าเริ่มต้นคือ timeout 15 นาทีต่อครั้ง และ retry อีก 1 ครั้งเมื่อ Codex ล้มเหลว

ดูคิวงานโดยไม่รันงาน:

```bash
python -m codex_worker --list
```

ปรับ timeout และจำนวน retry ได้:

```bash
python -m codex_worker --execute --timeout 900 --retries 1
```

หรือระบุไฟล์งาน:

```bash
python -m codex_worker --execute jobs/inbox/example.md
```

## รูปแบบงาน

สร้างไฟล์ Markdown ใน `jobs/inbox/` เช่น:

```markdown
# สรุปไฟล์รายงาน

อ่านไฟล์ใน `workspace/` แล้วเขียนสรุปภาษาไทยลงใน `outputs/summary.md`

เงื่อนไข:
- ห้ามแก้ไฟล์ต้นฉบับ
- ถ้าไม่พบไฟล์ ให้รายงานปัญหาและหยุด
```

เมื่อเริ่มงาน worker จะย้ายไฟล์ไป `jobs/processing/` และเมื่อจบจะย้ายไป `jobs/done/` หรือ `jobs/failed/`

ผลลัพธ์และ log จะอยู่ใน `runs/<job-id>/`

## ขอบเขตความปลอดภัย

- ค่าเริ่มต้นคือ dry-run
- ต้องใส่ `--execute` จึงจะเรียก Codex
- worker ใช้ lock กันการรันซ้อน และบันทึกสถานะเป็น `runs/<job-id>/status.json`
- งานที่ล้มเหลวจะ retry ตามจำนวนที่กำหนด แล้วจึงย้ายไป `jobs/failed/`
- environment เดิมของเครื่องถูกส่งให้ Codex เพื่อให้ CLI ใช้ session/config ที่ล็อกอินไว้ได้
- worker ส่ง prompt ที่กำหนดขอบเขตให้ Codex ทุกครั้ง
- ไม่ส่ง credential หรือ environment variables ทั้งหมดเข้าไปใน prompt
- ควรทดลองใน git branch/worktree แยกก่อนใช้กับโปรเจกต์จริง
- งานที่ส่งข้อความ, push, deploy, ลบข้อมูล หรือแก้ระบบภายนอกควรให้คนอนุมัติเอง

## โครงสร้าง

```text
AGENTS.md                 กติกาสำหรับ Codex
codex_worker/             ตัว worker
jobs/inbox/               งานที่รอทำ
jobs/processing/          งานที่กำลังทำ
jobs/done/                งานที่เสร็จแล้ว
jobs/failed/              งานที่ล้มเหลว
runs/                     output และ log ของแต่ละ job
workspace/                ไฟล์ input ที่อนุญาตให้ agent อ่าน
outputs/                  ผลงานที่ต้องการเก็บระยะยาว
```
