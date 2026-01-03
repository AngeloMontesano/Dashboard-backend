from fastapi import APIRouter

router = APIRouter(prefix="/roles", tags=["admin-roles"])

@router.get("")
async def admin_roles() -> list[str]:
    return ["tenant_admin", "staff", "readonly"]
