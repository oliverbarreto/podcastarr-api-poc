from fastapi import APIRouter, HTTPException

from ..services.channel_service import ChannelService
from ..core.logger import get_logger
from ..models.channel import ChannelUpdate

router = APIRouter(prefix="/channel", tags=["channel"])
logger = get_logger("routes.channel")
channel_service = ChannelService()


@router.get("")
async def get_channel():
    """Get the channel configuration."""
    try:
        channel = channel_service.get_channel()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return channel

    except Exception as e:
        logger.error(f"Error getting channel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_channel(channel_data: ChannelUpdate):
    """Create or update the channel configuration."""
    try:
        return channel_service.create_or_update_channel(
            channel_data.model_dump(exclude_unset=True)
        )

    except Exception as e:
        logger.error(f"Error updating channel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
