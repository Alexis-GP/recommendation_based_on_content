import cnocr
import numpy as np
from PIL import Image

# BV1Gz421q7HX

OCRmodel = cnocr.CnOcr()

# don't forget to optimise the codes, to avoid reload of the model in different objects.
class VidContent:
    def __init__(self,
                 bvid: str,
                 pic: str | Image.Image | np.ndarray | None=None,
                 user_name: str | None=None,
                 model=OCRmodel):
        assert 'BV' == bvid[:2], 'please provide correct BV id.'
        self.bvid = bvid
        self.pic = pic
        self.context = None
        self.model = model
        self.resize = (1080, 1920)
        self.pic_to_ocr = None
        self.content = None
        self.script = None


        if user_name is None:
            self.user_name = user_name
            # data.get_user_name(self.__name__)
        else:
            self.user_name = user_name

    def ocr(self):
        result = self.model.ocr(self.pic_to_ocr, resized_shape=self.resize)



    def new_pic(self, pic):
        self.pic.append(pic)
        self.pic_to_ocr = pic




    def clean(self):
        pass


    def save(self, save_pic=False):
        pass


