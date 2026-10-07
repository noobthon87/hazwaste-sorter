import io
import os
from PIL import Image
from app import app, save_and_resize_image
import database

# 1. Test Database
database.init_db()
print("[PASS] Database initialized")

# 2. Test Image resizing
large_img = Image.new("RGB", (2500, 1800), color="blue")
byte_io = io.BytesIO()
large_img.save(byte_io, "JPEG")
byte_io.seek(0)

filename = save_and_resize_image(byte_io)
saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
with Image.open(saved_path) as res_img:
    w, h = res_img.size
    assert max(w, h) <= 1024, f"Image not resized: {w}x{h}"
    print(f"[PASS] Resized large image (2500x1800) -> ({w}x{h}) <= 1024px")

# 3. Test Flask test client
client = app.test_client()

# GET /scan
r_scan = client.get("/scan")
assert r_scan.status_code == 200
assert b"Advisory only" in r_scan.data
assert b"Take Photo" in r_scan.data
assert b'capture="environment"' in r_scan.data
print("[PASS] /scan screen rendered")

# POST /classify
byte_io.seek(0)
r_post = client.post(
    "/classify",
    data={"photo": (byte_io, "camera_test.jpg"), "description": "Hydraulic fluid wipe"},
    content_type="multipart/form-data",
    follow_redirects=True
)
assert r_post.status_code == 200
assert b"Classification Result" in r_post.data
assert b"YELLOW" in r_post.data or b"Yellow" in r_post.data or b"Chemical" in r_post.data
print("[PASS] /classify processed and redirected to result")

# GET /log
r_log = client.get("/log")
assert r_log.status_code == 200
assert b"Hangar Waste Log" in r_log.data
print("[PASS] /log screen rendered")

# Check database records
records = database.get_all_records()
assert len(records) >= 1
print(f"[PASS] SQLite records verified: {len(records)} found")

print("[SUCCESS] All Version 1 requirements verified!")
