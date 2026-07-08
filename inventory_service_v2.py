from typing import Optional

import pandas as pd
from sqlalchemy import text

from db import engine


class InventoryService:
    """
    Inventory Service V2

    Handles inventory movements:
    - Receipts
    - Consumption
    - Production Outputs
    - Stage Production Execution
    - Current Stock
    - Transaction History
    """

    # =====================================================
    # RECEIPTS
    # =====================================================

    def receive_material(
        self,
        material_code: str,
        quantity: float,
        reference: Optional[str] = None,
        created_by: Optional[str] = None,
    ):
        try:
            stage_code = self._get_stage_code(material_code)

            item = self._find_item(
                material_code=material_code,
                stage_code=stage_code,
            )

            if item is None:
                return {
                    "success": False,
                    "message": f"Item '{material_code}' not found.",
                    "data": None,
                }

            self._apply_inventory_transaction(
                item_id=int(item["item_id"]),
                quantity=quantity,
                transaction_type="RECEIPT",
                reference_doc=reference,
                notes="Material Receipt",
                created_by=created_by,
            )

            return {
                "success": True,
                "message": "Material received successfully.",
                "data": {"item_id": int(item["item_id"])},
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None,
            }

    # =====================================================
    # CONSUMPTION
    # =====================================================

    def consume_material(
        self,
        material_code: str,
        quantity: float,
        work_order_id: Optional[int] = None,
        created_by: Optional[str] = None,
    ):
        try:
            stage_code = self._get_stage_code(material_code)

            item = self._find_item(
                material_code=material_code,
                stage_code=stage_code,
            )

            if item is None:
                return {
                    "success": False,
                    "message": f"Item '{material_code}' not found.",
                    "data": None,
                }

            current_stock = float(item["stock_on_hand"])

            if current_stock < quantity:
                return {
                    "success": False,
                    "message": (
                        f"Insufficient stock for {material_code}. "
                        f"Available: {current_stock}, Requested: {quantity}"
                    ),
                    "data": None,
                }

            self._apply_inventory_transaction(
                item_id=int(item["item_id"]),
                quantity=-quantity,
                transaction_type="CONSUMPTION",
                reference_doc=f"WO-{work_order_id}" if work_order_id else None,
                notes="Material Consumption",
                created_by=created_by,
            )

            return {
                "success": True,
                "message": "Material consumed successfully.",
                "data": {
                    "item_id": int(item["item_id"]),
                    "quantity": quantity,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None,
            }

    # =====================================================
    # PRODUCTION OUTPUT
    # =====================================================

    def produce_item(
        self,
        material_code: str,
        quantity: float,
        work_order_id: Optional[int] = None,
        created_by: Optional[str] = None,
    ):
        try:
            stage_code = self._get_stage_code(material_code)

            item = self._find_item(
                material_code=material_code,
                stage_code=stage_code,
            )

            if item is None:
                return {
                    "success": False,
                    "message": f"Item '{material_code}' not found.",
                    "data": None,
                }

            self._apply_inventory_transaction(
                item_id=int(item["item_id"]),
                quantity=quantity,
                transaction_type="PRODUCTION",
                reference_doc=f"WO-{work_order_id}" if work_order_id else None,
                notes="Production Output",
                created_by=created_by,
            )

            return {
                "success": True,
                "message": "Production completed successfully.",
                "data": {
                    "item_id": int(item["item_id"]),
                    "quantity": quantity,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None,
            }

    # =====================================================
    # STAGE PRODUCTION
    # =====================================================

    def execute_stage_production(
        self,
        stage_id: int,
        model: str,
        quantity: float,
        work_order_id: Optional[int] = None,
        created_by: Optional[str] = None,
    ):
        try:
            model = model.strip()

            inputs = self._get_stage_inputs(
                stage_id=stage_id,
                model=model,
            )

            consumed = 0

            for _, row in inputs.iterrows():
                result = self.consume_material(
                    material_code=row["material_code"],
                    quantity=float(row["quantity_per_unit"]) * quantity,
                    work_order_id=work_order_id,
                    created_by=created_by,
                )

                if not result["success"]:
                    return result

                consumed += 1

            outputs = self._get_stage_outputs(
                stage_id=stage_id,
                model=model,
            )

            produced = 0

            for _, row in outputs.iterrows():
                result = self.produce_item(
                    material_code=row["output_material"],
                    quantity=float(row["output_qty"]) * quantity,
                    work_order_id=work_order_id,
                    created_by=created_by,
                )

                if not result["success"]:
                    return result

                produced += 1

            return {
                "success": True,
                "message": "Stage production completed successfully.",
                "data": {
                    "inputs_consumed": consumed,
                    "outputs_produced": produced,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None,
            }

    # =====================================================
    # ADJUSTMENTS
    # =====================================================

    def adjust_stock(
        self,
        material_code: str,
        quantity: float,
        reason: str,
        created_by: Optional[str] = None,
    ):
        try:
            stage_code = self._get_stage_code(material_code)

            item = self._find_item(
                material_code=material_code,
                stage_code=stage_code,
            )

            if item is None:
                return {
                    "success": False,
                    "message": f"Item '{material_code}' not found.",
                    "data": None,
                }

            self._apply_inventory_transaction(
                item_id=int(item["item_id"]),
                quantity=quantity,
                transaction_type="ADJUSTMENT",
                reference_doc=None,
                notes=reason,
                created_by=created_by,
            )

            return {
                "success": True,
                "message": "Stock adjusted successfully.",
                "data": {"item_id": int(item["item_id"])},
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None,
            }

    # =====================================================
    # TRANSFERS
    # =====================================================

    def transfer_stock(
        self,
        material_code: str,
        from_stage: str,
        to_stage: str,
        quantity: float,
    ):
        raise NotImplementedError

    # =====================================================
    # QUERIES
    # =====================================================

    def get_current_stock(
        self,
        material_code: str,
    ) -> pd.DataFrame:
        query = """
            SELECT
                item_id,
                material_code,
                stage_code,
                item_name,
                item_type,
                current_stock,
                unit
            FROM vw_currentstock
            WHERE material_code = :material_code
            ORDER BY stage_code
        """

        return pd.read_sql(
            text(query),
            engine,
            params={"material_code": material_code},
        )

    def get_item_transactions(
        self,
        material_code: str,
    ) -> pd.DataFrame:
        query = """
            SELECT
                t.transaction_id,
                i.material_code,
                i.stage_code,
                i.item_name,
                t.transaction_type,
                t.quantity,
                t.reference_doc,
                t.notes,
                t.transaction_date,
                t.created_by
            FROM stocktransactions t
            INNER JOIN items i
                ON i.item_id = t.item_id
            WHERE i.material_code = :material_code
            ORDER BY
                t.transaction_date DESC,
                t.transaction_id DESC
        """

        return pd.read_sql(
            text(query),
            engine,
            params={"material_code": material_code},
        )

    # =====================================================
    # PRIVATE HELPERS
    # =====================================================

    def _get_stage_code(
        self,
        material_code: str,
    ) -> str:
        if "|" in material_code:
            return material_code.split("|")[1].strip()

        return "RAW"

    def _find_item(
        self,
        material_code: str,
        stage_code: str = "RAW",
    ):
        query = """
            SELECT
                item_id,
                material_code,
                stage_code,
                item_name,
                item_type,
                stock_on_hand
            FROM items
            WHERE material_code = :material_code
              AND stage_code = :stage_code
        """

        df = pd.read_sql(
            text(query),
            engine,
            params={
                "material_code": material_code,
                "stage_code": stage_code,
            },
        )

        if df.empty:
            return None

        return df.iloc[0]

    def _get_stage_inputs(
        self,
        stage_id: int,
        model: str,
    ) -> pd.DataFrame:
        query = """
            SELECT
                material_code,
                quantity_per_unit
            FROM stage_inputs
            WHERE stage_id = :stage_id
              AND LOWER(model) = LOWER(:model)
        """

        return pd.read_sql(
            text(query),
            engine,
            params={
                "stage_id": stage_id,
                "model": model,
            },
        )

    def _get_stage_outputs(
        self,
        stage_id: int,
        model: str,
    ) -> pd.DataFrame:
        query = """
            SELECT
                output_material,
                output_qty
            FROM stage_outputs
            WHERE stage_id = :stage_id
              AND LOWER(model) = LOWER(:model)
        """

        return pd.read_sql(
            text(query),
            engine,
            params={
                "stage_id": stage_id,
                "model": model,
            },
        )

    def _apply_inventory_transaction(
        self,
        item_id: int,
        quantity: float,
        transaction_type: str,
        reference_doc=None,
        notes=None,
        created_by=None,
    ):
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE items
                    SET stock_on_hand = stock_on_hand + :quantity
                    WHERE item_id = :item_id
                """),
                {
                    "item_id": item_id,
                    "quantity": quantity,
                },
            )

            conn.execute(
                text("""
                    INSERT INTO stocktransactions
                    (
                        item_id,
                        transaction_type,
                        quantity,
                        reference_doc,
                        notes,
                        created_by
                    )
                    VALUES
                    (
                        :item_id,
                        :transaction_type,
                        :quantity,
                        :reference_doc,
                        :notes,
                        :created_by
                    )
                """),
                {
                    "item_id": item_id,
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "reference_doc": reference_doc,
                    "notes": notes,
                    "created_by": created_by,
                },
            )

    # =====================================================
    # MAINTENANCE
    # =====================================================

    def rebuild_inventory(self):
        raise NotImplementedError


if __name__ == "__main__":
    inventory = InventoryService()

    result = inventory.get_current_stock(
        "0025-0373|RAW"
    )

    print(result)