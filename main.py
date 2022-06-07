import streamlit as st
import io
from PIL import Image
import requests

st.set_page_config(
    page_title="빨간 알약 줄까? 파란 알약 줄까?", layout="centered", page_icon="pill"
)


def main():

    st.image(Image.open("images/bald.jpg"))

    st.sidebar.title("사용법")
    st.sidebar.subheader("1. 알아보고 싶은 알약의 앞면과 뒷면이 잘 보이도록 사진을 각각 한 장씩 찍습니다.")
    st.sidebar.subheader("2. 찍은 알약의 앞면 사진을 상단에, 뒷면 사진을 하단에 업로드합니다.")
    st.sidebar.subheader("3. 알약 영역이 잘 분리되었는지 확인해줍니다.")
    st.sidebar.subheader("4. 사진이 잘 분리되었다면 예측 시작 버튼을 누릅니다.")
    st.sidebar.subheader("5. 업로드한 사진과 유사한 알약을 k개까지 웹페이지 상으로 보여줍니다.")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    uploaded_file_front = col1.file_uploader(
        "알약 앞면 사진을 올려주세요.", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file_front:
        image_bytes = uploaded_file_front.getvalue()
        image = Image.open(io.BytesIO(image_bytes))
        col3.image(image, caption="Pill front")
        res = requests.post('http://127.0.0.1:8080/image_segment', files = {'file':image_bytes})
        seg_front = res.content
        seg_front_img = Image.open(io.BytesIO(seg_front))
        col5.image(seg_front_img, caption='Pill front')


    uploaded_file_back = col2.file_uploader(
        "알약 뒷면 사진을 올려주세요.", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file_back:
        image_bytes = uploaded_file_back.getvalue()
        image = Image.open(io.BytesIO(image_bytes))
        col4.image(image, caption="Pill back")
        res = requests.post('http://127.0.0.1:8080/image_segment', files = {'file':image_bytes})
        seg_back = res.content
        seg_back_img = Image.open(io.BytesIO(seg_back))
        col6.image(seg_back_img, caption='Pill back')

    if uploaded_file_front and uploaded_file_back:
        if st.button("예측 시작"):

            files = [
                ("files", seg_front),
                ("files", seg_back),
            ]
            res = requests.post("http://127.0.0.1:8080/image_query/", files=files)

            outputs = res.json()
            outn = min(len(outputs["items"]), 5)
            outputs = outputs["items"]
            cols = st.columns(outn)
            for i in range(outn):
                output = outputs[i]
                response = requests.get(output['image_url'])
                img = Image.open(io.BytesIO(response.content))
                cols[i].write(f"{i+1}. {output['name']}")
                cols[i].image(img)
                cols[i].write(f"효능: {output['usage']}")
                cols[i].write(f"유사도: {output['score']}")


main()
