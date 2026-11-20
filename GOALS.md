# Goals

## Purpose

สร้าง local worker ที่รับงานแบบ text จากไฟล์ Markdown แล้วส่งให้ Codex CLI ทำงานใน repository อย่างมีขอบเขต ตรวจสอบได้ และกู้คืนได้เมื่อเกิดข้อผิดพลาด

## Desired outcomes

- สร้าง job ได้โดยไม่ต้องแก้ source code ของ worker
- ทุก job มีสถานะ, log และผลลัพธ์ที่ตรวจสอบย้อนหลังได้
- งานเสี่ยง เช่น push, deploy, ส่งข้อความ หรือลบข้อมูล ต้องหยุดรอมนุษย์
- workflow ที่ใช้ซ้ำถูกเก็บเป็น Codex skill

## Scope

- รับ job จาก `jobs/inbox/`
- เรียก Codex CLI แบบ bounded execution
- เก็บหลักฐานใน `runs/` และผลงานใน `outputs/`
- รองรับ skills สำหรับ workflow ที่ทำซ้ำ

## Non-goals for the current phase

- voice input/output
- Telegram, Slack หรือ web UI
- autonomous push/deploy
- multi-agent orchestration
- การเข้าถึง credential หรือข้อมูลนอก repository

## Success criteria

- job ตัวอย่างทำ dry-run ได้
- job ที่รันจริงมี `status.json`, stdout/stderr และผลลัพธ์
- job ที่ล้มเหลวไม่ค้างเป็นงานใหม่ใน inbox
- Codex เห็นกติกาจาก `AGENTS.md` และ skill ที่เกี่ยวข้อง
