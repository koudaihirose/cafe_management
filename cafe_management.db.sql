BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "category" (
	"id"	INTEGER,
	"category_name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "product" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"category_id"	INTEGER,
	"image_url"	TEXT,
	"notes"	TEXT,
	"price"	REAL,
	"is_deleted"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("category_id") REFERENCES "category"("id")
);
CREATE TABLE IF NOT EXISTS "staff" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "stock_movement" (
	"id"	INTEGER,
	"product_id"	INTEGER NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"movement_date"	DATE NOT NULL,
	"staff_id"	INTEGER NOT NULL,
	"movement_type"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("product_id") REFERENCES "product"("id"),
	FOREIGN KEY("staff_id") REFERENCES "staff"("id")
);
INSERT INTO "product" VALUES (1,'a',1,'uploads/image2.jpg','',NULL,0);
INSERT INTO "product" VALUES (2,'コーヒー２',1,'uploads/image1.jpg','',NULL,0);
INSERT INTO "product" VALUES (4,'coffee',1,NULL,'',2000.0,1);
INSERT INTO "staff" VALUES (1,'hirose');
INSERT INTO "stock_movement" VALUES (1,1,1,'2024-09-26 15:12:54',1,'入庫');
COMMIT;
