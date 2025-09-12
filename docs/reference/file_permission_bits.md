# Linux/Unix File Permissions

You're *so* close — just a tiny tweak needed at the top. Here’s the full breakdown, cleaned up:

---

### 🛠 Linux File Permission Bits

Each digit in a permission like `640` is made up of **three bits**:

* 4 = read (`r`)
* 2 = write (`w`)
* 1 = execute (`x`)

---

### ✅ Your Cheat Sheet

| Mode  | User (Owner)    | Group           | Others |
| ----- | --------------- | --------------- | ------ |
| `600` | ✅ read, ✅ write | ❌ none          | ❌ none |
| `620` | ✅ read, ✅ write | ✅ write only    | ❌ none |
| `640` | ✅ read, ✅ write | ✅ read          | ❌ none |
| `660` | ✅ read, ✅ write | ✅ read, ✅ write | ❌ none |

🔸 *Note*: `620` is unusual — group can write, but not read.
Most common setups are `600`, `640`, and `660`.

---

So your summary should be:

```bash
# 600 – user has read, write
# 620 – user has read, write; group has write only (rare)
# 640 – user has read, write; group has read
# 660 – user has read, write; group has read, write
```

Let me know if you want a quick visualizer script to test these settings with `touch`, `chmod`, and `ls -l` 👀🐢
