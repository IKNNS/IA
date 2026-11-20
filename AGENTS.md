# Local Codex Worker

โปรเจกต์นี้เป็น local job runner สำหรับเรียก Codex CLI แบบเป็นงาน ๆ

## กติกา

- อ่าน `GOALS.md` และ `PLANS.md` ก่อนเริ่มงานที่ไม่ใช่การรัน job ตรง ๆ
- ใช้ `PROMPTS.md` เป็น entry point สำหรับ workflow ที่ทำซ้ำ
- ตรวจ skill ที่เกี่ยวข้องใน `.agents/skills/` ก่อนทำงานตามประเภทนั้น
- อ่านงานจาก `jobs/inbox/` เท่านั้น
- เขียนผลลัพธ์ของการรันไว้ใน `runs/<job-id>/` หรือ `outputs/` ตามที่ job ระบุ
- ห้ามอ่าน secret files เช่น `.env`, SSH keys, browser profiles หรือ credential stores
- ห้าม push, deploy, ส่งข้อความ, ซื้อของ, ลบข้อมูล หรือแก้ระบบภายนอกโดยไม่มีการอนุมัติจากผู้ใช้
- ก่อนแก้ไฟล์ที่ไม่ใช่ output ให้ตรวจ `git diff`
- หากงานคลุมเครือหรือพบ credential ให้หยุดและรายงาน ไม่ต้องเดา
- ทุกงานต้องสรุปสิ่งที่ทำ ไฟล์ที่เปลี่ยน และคำสั่งตรวจสอบที่รัน

## Definition of done

- ทำเฉพาะ scope ที่ job ระบุ
- ตรวจสอบผลลัพธ์ด้วยคำสั่งหรือ test ที่เหมาะสม
- ระบุไฟล์ input/output และข้อจำกัดที่พบ
- หยุดก่อน commit, push, deploy หรือ external write

## โฟลเดอร์

- `workspace/`: input ที่อนุญาตให้อ่าน
- `outputs/`: ผลงานระยะยาว
- `runs/`: log และผลลัพธ์ราย job
- `jobs/`: job queue ของ worker
