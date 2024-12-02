import pytesseract
from PIL import Image
import re

# Tesseract 경로 설정 (만약 다른 경로에 설치되어 있다면 변경해야 함)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def extract_total_amount_from_image(image_path):
    """
    이미지에서 금액을 추출하여 반환하는 함수.
    이미지에서 쉼표가 포함된 금액을 찾고 가장 큰 값을 반환합니다.
    """
    # 이미지 열기
    img = Image.open(image_path)

    # pytesseract로 텍스트 추출
    result = pytesseract.image_to_string(img, lang='kor')

    # 쉼표가 포함된 금액 추출을 위한 정규식 (숫자와 쉼표 포함된 부분)
    numbers_with_commas = re.findall(r'\d{1,3}(?:,\d{3})*', result)

    # 쉼표를 제거하고 정수로 변환하여 리스트에 저장
    numbers = [int(num.replace(',', '')) for num in numbers_with_commas]

    if numbers:
        # 가장 큰 금액을 찾아 반환
        return max(numbers)
    else:
        print("이미지에서 금액을 추출할 수 없습니다.")
        return None

def split_bill_from_image(image_path, num_people):
    """
    이미지에서 금액을 추출하여 나누어 1인당 금액을 출력하는 함수.
    """
    total_amount = extract_total_amount_from_image(image_path)

    if total_amount is not None:
        if num_people <= 0:
            print("인원 수는 1명 이상이어야 합니다.")
        else:
            # 1인당 금액 계산
            amount_per_person = total_amount / num_people
            
            # 쉼표 형식으로 금액 포맷팅
            formatted_total = f"{total_amount:,} 원"
            formatted_per_person = f"{amount_per_person:,.0f} 원"  # 소수점 이하 제거
            
            print(f"총 금액: {formatted_total}")
            print(f"1인당 금액: {formatted_per_person}")
    else:
        print("유효한 금액을 추출할 수 없습니다.")





import random
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock


class GuessGameApp(App):
    def __init__(self, images=None, **kwargs):
        super().__init__(**kwargs)
        self.images = images or []  # 사용자 정의 이미지를 받거나 기본값으로 빈 리스트 사용
        self.selected_images = []
        self.num_questions = 0
        self.num_input = None
        self.text_input = None

    def build(self):
        if not self.images:
            raise ValueError("이미지 데이터가 없습니다. 'images' 인수를 사용해 데이터를 전달하세요.")
        
        self.current_index = 0
        self.score = 0
        self.root = FloatLayout()
        return self.show_question_input_screen()

    def show_question_input_screen(self):
        self.root.clear_widgets()
        background = Image(source="술게임 이미지파일.jpg", allow_stretch=True, keep_ratio=False)
        self.root.add_widget(background)

        content = BoxLayout(orientation="vertical", size_hint=(0.8, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.5})

        self.error_label = Label(
            text="풀 문제의 수를 입력하세요", font_name="NanumGothic.ttf",
            size_hint=(1, 0.3), font_size="30sp", color=(0, 0, 0, 1)
        )
        content.add_widget(self.error_label)

        self.num_input = TextInput(
            hint_text="숫자를 입력하세요", multiline=False, input_filter="int",
            size_hint=(1, 0.3), font_name="NanumGothic.ttf"
        )
        self.num_input.bind(on_text_validate=self.start_game)
        content.add_widget(self.num_input)

        start_button = Button(text="시작", size_hint=(1, 0.4), font_name="NanumGothic.ttf")
        start_button.bind(on_press=self.start_game)
        content.add_widget(start_button)

        self.root.add_widget(content)

        # Clock을 사용해 입력창 자동 활성화
        Clock.schedule_once(self.activate_start_input, 0.1)
        return self.root

    def activate_start_input(self, *args):
        """시작 화면의 입력창 자동 활성화"""
        if self.num_input:
            self.num_input.focus = True

    def start_game(self, instance):
        try:
            self.num_questions = int(self.num_input.text.strip())
        except ValueError:
            self.error_label.text = "유효하지 않은 입력입니다. 숫자를 다시 입력해주세요."
            self.error_label.color = (1, 0, 0, 1)
            Clock.schedule_once(self.activate_start_input, 0.1)  # 잘못된 입력 후 포커스 재설정
            return

        if self.num_questions <= 0 or self.num_questions > len(self.images):
            self.error_label.text = f"문제 수는 1에서 {len(self.images)} 사이여야 합니다."
            self.error_label.color = (1, 0, 0, 1)
            Clock.schedule_once(self.activate_start_input, 0.1)  # 잘못된 입력 후 포커스 재설정
            return

        random.shuffle(self.images)
        self.selected_images = self.images[:self.num_questions]

        self.current_index = 0
        self.score = 0

        self.show_game_screen()

    def show_game_screen(self):
        self.root.clear_widgets()

        background = Image(source="술게임 이미지파일.jpg", allow_stretch=True, keep_ratio=False)
        self.root.add_widget(background)

        content = BoxLayout(orientation="vertical", size_hint=(0.8, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.375})

        self.image = Image(source=self.selected_images[self.current_index]["image"], size_hint=(1, 0.6))
        content.add_widget(self.image)

        if not self.text_input:
            self.text_input = TextInput(
                hint_text="정답을 입력하세요", multiline=False, size_hint=(0.5, 0.06),
                pos_hint={"center_x": 0.5}, font_name="NanumGothic.ttf"
            )
            self.text_input.bind(on_text_validate=self.check_answer)
        self.text_input.text = ""  # 입력값 초기화
        content.add_widget(self.text_input)

        self.submit_button = Button(
            text="제출", size_hint=(0.5, 0.06),
            pos_hint={"center_x": 0.5}, font_name="NanumGothic.ttf"
        )
        self.submit_button.bind(on_press=self.check_answer)
        content.add_widget(self.submit_button)

        self.result_label = Label(text="", size_hint=(1, 0.2), font_name="NanumGothic.ttf")
        content.add_widget(self.result_label)

        self.root.add_widget(content)

        # Clock을 사용해 입력창 포커스 설정
        Clock.schedule_once(self.set_focus, 0.1)

    def set_focus(self, *args):
        """게임 화면의 입력창 활성화"""
        if self.text_input:
            self.text_input.focus = True

    def check_answer(self, instance):
        user_input = self.text_input.text.strip()
        correct_answer = self.selected_images[self.current_index]["answer"]

        if user_input == correct_answer:
            self.result_label.text = "정답입니다!"
            self.result_label.color = (0, 1, 0, 1)
            self.score += 1
        else:
            self.result_label.text = f"마셔!!!! 정답은 '{correct_answer}'였습니다."
            self.result_label.color = (1, 0, 0, 1)

        self.current_index += 1
        if self.current_index < self.num_questions:
            self.image.source = self.selected_images[self.current_index]["image"]
            self.text_input.text = ""  # 입력창 초기화
            Clock.schedule_once(self.set_focus, 0.1)  # 다음 문제에서도 포커스 설정
        else:
            self.result_label.text = f"게임 종료! 점수: {self.score}/{self.num_questions}"
            self.text_input.disabled = True
            self.submit_button.disabled = True


# Example usage
# custom_images = [
#     {"image": "태양사진.jpg", "answer": "태양"},
#     {"image": "지디사진.jpg", "answer": "지디"},
#     {"image": "대성사진.jpg", "answer": "대성"},
#     {"image": "박보검.jpg", "answer": "박보검"},
#     {"image": "설윤.jpg", "answer": "설윤"},
#     {"image": "윈터.jpg", "answer": "윈터"},
#     {"image": "유재석.jpg", "answer": "유재석"},
#     {"image": "장성규.jpg", "answer": "장성규"},
#     {"image": "조세호.jpg", "answer": "조세호"},
#     {"image": "차은우.jpg", "answer": "차은우"},
# ]

# GuessGameApp(images=custom_images).run()

