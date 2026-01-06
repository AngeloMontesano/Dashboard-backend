"""seed units and sample categories/items

Revision ID: 0010_seed_units_and_templates
Revises: 0009_create_inventory_orders
Create Date: 2026-01-08 13:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0010_seed_units_and_templates"
down_revision = "0009_create_inventory_orders"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "item_units",
        sa.Column("code", sa.String(length=32), primary_key=True),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.execute(
        """
        INSERT INTO item_units (code, label, is_active) VALUES
        ('pcs', 'Stück', TRUE),
        ('pkg', 'Packung', TRUE),
        ('kg', 'Kilogramm', TRUE),
        ('g', 'Gramm', TRUE),
        ('l', 'Liter', TRUE),
        ('ml', 'Milliliter', TRUE),
        ('slice', 'Scheibe', TRUE),
        ('scoop', 'Eiskugel', TRUE)
        ON CONFLICT (code) DO NOTHING;
        """
    )

    op.execute(
        """
        DO $$
        DECLARE
            tid uuid;
            cat_bread uuid;
            cat_pastry uuid;
            cat_ice uuid;
            cat_topping uuid;
        BEGIN
            SELECT id INTO tid FROM tenants WHERE slug = 'kunde1' LIMIT 1;
            IF tid IS NULL THEN
                RETURN;
            END IF;

            INSERT INTO categories (id, tenant_id, name, is_system, is_active)
            VALUES
                (gen_random_uuid(), tid, 'Brot & Brötchen', FALSE, TRUE),
                (gen_random_uuid(), tid, 'Gebäck & Kuchen', FALSE, TRUE),
                (gen_random_uuid(), tid, 'Eis & Grundmassen', FALSE, TRUE),
                (gen_random_uuid(), tid, 'Toppings & Soßen', FALSE, TRUE)
            ON CONFLICT DO NOTHING;

            SELECT id INTO cat_bread FROM categories WHERE tenant_id = tid AND name = 'Brot & Brötchen' LIMIT 1;
            SELECT id INTO cat_pastry FROM categories WHERE tenant_id = tid AND name = 'Gebäck & Kuchen' LIMIT 1;
            SELECT id INTO cat_ice FROM categories WHERE tenant_id = tid AND name = 'Eis & Grundmassen' LIMIT 1;
            SELECT id INTO cat_topping FROM categories WHERE tenant_id = tid AND name = 'Toppings & Soßen' LIMIT 1;

            INSERT INTO items (
                id, tenant_id, sku, barcode, name, description,
                category_id, quantity, min_stock, max_stock, target_stock, recommended_stock,
                order_mode, unit, is_active
            ) VALUES
                (gen_random_uuid(), tid, 'BROT-001', '400000000001', 'Roggenmischbrot 1kg', 'Standardlaib Roggenmischbrot', cat_bread, 20, 5, 50, 30, 25, 0, 'kg', TRUE),
                (gen_random_uuid(), tid, 'BRCH-001', '400000000002', 'Laugenbrezel', 'Frischgebackene Brezeln', cat_bread, 200, 50, 500, 300, 250, 0, 'pcs', TRUE),
                (gen_random_uuid(), tid, 'KUCH-001', '400000000003', 'Apfelkuchen Blech', 'Blechkuchen mit Äpfeln', cat_pastry, 8, 2, 20, 12, 10, 0, 'slice', TRUE),
                (gen_random_uuid(), tid, 'EIS-BASE-001', '400000000004', 'Eis-Basismix Vanille 5L', 'Grundmasse für Vanilleeis', cat_ice, 5, 1, 15, 10, 8, 0, 'l', TRUE),
                (gen_random_uuid(), tid, 'TOP-CHOCO-001', '400000000005', 'Schokoladensoße', 'Topping für Eisbecher', cat_topping, 10, 2, 30, 15, 12, 0, 'ml', TRUE)
            ON CONFLICT (tenant_id, sku) DO NOTHING;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.drop_table("item_units")
