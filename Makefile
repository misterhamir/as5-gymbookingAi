

server:
	uvicorn app.main:app --reload

seed:
	python seed_db.py

streamlit:
	streamlit run streamlit_app.py

