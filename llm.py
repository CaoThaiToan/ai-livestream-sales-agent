import time
from typing import TYPE_CHECKING

from agent.service import answer_question
from utils.logger import logger

if TYPE_CHECKING:
    from avatars.base_avatar import BaseAvatar


def llm_response(message, avatar_session: 'BaseAvatar', datainfo: dict = {}):
    start = time.perf_counter()
    session_id = str(getattr(avatar_session, 'sessionid', 'livestream'))

    try:
        response = answer_question(session_id, message)
        answer = response.get('answer', '').strip()
        status = response.get('status', 'error')
        product_ids = response.get('product_ids', [])

        logger.info(
            "Sales agent status=%s product_ids=%s elapsed=%.3fs",
            status,
            product_ids,
            time.perf_counter() - start,
        )

        if answer:
            avatar_session.put_msg_txt(answer, datainfo)
    except Exception:
        logger.exception('Sales agent response failed')
        avatar_session.put_msg_txt(
            'Dạ hệ thống đang gặp trục trặc, bạn vui lòng thử lại sau ạ.',
            datainfo,
        )
