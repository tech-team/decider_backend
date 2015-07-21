import httplib
from PIL import Image, ImageOps
import uuid
from django.utils import timezone
import os
from oauth2_provider.views import ProtectedResourceView
import re
from decider_api.utils.endpoint_decorators import require_params
from decider_api.utils.image_helper import IMAGE_SIZE
from decider_app.models import Question, PollItem
from decider_app.views.utils.response_builder import build_response, build_error_response
from decider_app.views.utils.response_codes import CODE_CREATED, CODE_UNKNOWN_QUESTION
from decider_backend.settings import MEDIA_ROOT, STATIC_ROOT


class ShareEndpoint(ProtectedResourceView):

    BORDER_SIZE = 15
    OFFSETS = ((78, 50), (1210, 50))

    @require_params(['question_id'])
    def post(self, request, *args, **kwargs):
        bg = Image.open(os.path.join(STATIC_ROOT, "img", "share.png"))
        logo = Image.open(os.path.join(STATIC_ROOT, "img", "logo.png"))
        logo_offset = ((self.OFFSETS[1][0] + self.OFFSETS[0][0] + IMAGE_SIZE[0] - logo.size[0])//2,
                       self.OFFSETS[0][1] + IMAGE_SIZE[1] - logo.size[1])

        question_id = int(request.POST.get('question_id'))

        pi = PollItem.objects.filter(question_id=question_id).order_by('id')
        if not pi:
            return build_error_response(httplib.NOT_FOUND, CODE_UNKNOWN_QUESTION, "Question unknown")

        image_size = (IMAGE_SIZE[0] - self.BORDER_SIZE, IMAGE_SIZE[1] - self.BORDER_SIZE)
        left_img = ImageOps.expand(Image.open(os.path.join(MEDIA_ROOT, re.sub("media/?", "", pi[0].picture.url)))
                                   .resize(image_size), border=15, fill='grey')
        right_img = ImageOps.expand(Image.open(os.path.join(MEDIA_ROOT, re.sub("media/?", "", pi[1].picture.url)))
                                    .resize(image_size), border=15, fill='grey')

        bg.paste(left_img, self.OFFSETS[0])
        bg.paste(right_img, self.OFFSETS[1])
        bg.paste(logo, logo_offset, logo)

        cur_time = timezone.now().strftime('%s')
        uid = uuid.uuid4().hex
        filename = uid + '.jpg'
        dirname = os.path.join('images', 'share', cur_time[:5], cur_time[5:6])
        url = os.path.join(dirname, filename)

        if not os.path.exists(os.path.join(MEDIA_ROOT, dirname)):
            os.makedirs(os.path.join(MEDIA_ROOT, dirname))

        bg.save(os.path.join(MEDIA_ROOT, url), 'JPEG', quality=95)

        return build_response(httplib.CREATED, CODE_CREATED, "Sharing image created",
                              {"url": os.path.join('media', url)})