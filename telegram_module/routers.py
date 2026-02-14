from aiogram import Router
from handlers import router as handlers_router
from handlers import authorized_router

router = Router()
router.include_router(handlers_router)
router.include_router(authorized_router)
