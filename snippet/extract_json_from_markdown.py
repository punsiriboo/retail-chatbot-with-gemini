import re

# Sample markdown text containing JSON block
markdown_str = """
Some text in markdown.
```json
{"explaination": "รูปภาพแสดงให้เห็นถึงเครื่องดื่มโปรตีนจากพืชยี่ห้อ HooRay! รสช็อกโกแลตเบลเยี่ยม  บรรจุในขวดพลาสติก  มีปริมาณโปรตีน 30 กรัมต่อขวด  ไม่มีน้ำตาลซูโครส  และมีส่วนผสมของน้ำมัน MCT วิตามิน และแร่ธาตุต่างๆ", "is_retail_product": true, "product_description": "เครื่องดื่มโปรตีนจากพืช"}
```
"""

pattern = r"(json)\s*(\{.*?\})\s*"
match = re.search(pattern, markdown_str, re.DOTALL)
if match:
    json_str = match.group(2)
    print(f"Extracted Group 2 (JSON Block):\n{json_str}")
else:
    print("No match found.")
