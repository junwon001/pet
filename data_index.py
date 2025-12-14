from sentence_transformers import SentenceTransformer
import chromadb
import pandas as pd
import os

# --- 1. 환경 설정 및 변수 정의 ---
# 🚨 KoELECTRA 기반 모델 설정 🚨
# 'monologg/koelectra-base-v3-discriminator' 기반으로 훈련된 SBERT 모델을 사용합니다.
# 이는 KoELECTRA의 강력한 성능을 문장 임베딩에 활용한 모델입니다.
EMBEDDING_MODEL_NAME = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS' 
# 다른 강력한 한국어 임베딩 모델 예시: 'BM-K/KoSimCSE-RoBERTa-base'

# 입력 데이터 파일 및 Chroma DB 설정
CSV_FILE = 'final_rag_data_combined_raw.csv'  # 인덱싱할 원본 데이터 파일
COLLECTION_NAME = 'koelectra_pet_knowledge_index'  # Chroma DB에 저장될 컬렉션 이름
DB_PATH = "./chroma_db_koelectra"  # Chroma DB가 영구 저장될 디렉토리

# ---------------------------------

# 2. 임베딩 모델 로드
print(f"✅ 임베딩 모델 로딩 시작: **{EMBEDDING_MODEL_NAME}**")
try:
    # SentenceTransformer를 사용하여 KoELECTRA 기반 SBERT 모델 로드
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("✅ 모델 로드 성공.")
except Exception as e:
    print(f"❌ 오류: 모델 로드 실패. '{EMBEDDING_MODEL_NAME}' 모델을 Hugging Face에서 찾을 수 없거나 호환되지 않습니다.")
    print(f"세부 오류: {e}")
    exit()

# 3. 데이터 로드
try:
    # CSV 파일에서 데이터프레임(DataFrame) 로드
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    print(f"✅ 데이터 로드 성공: '{CSV_FILE}'에서 총 {len(df)}개 청크 확인.")
except FileNotFoundError:
    print(f"❌ 오류: '{CSV_FILE}' 파일을 찾을 수 없습니다. 파일 경로 및 이름을 확인하세요.")
    exit()

# 4. Chroma DB 클라이언트 초기화 및 컬렉션 준비
# 지정된 경로에 Chroma DB 영구 저장소 설정
client = chromadb.PersistentClient(path=DB_PATH)
# 컬렉션 이름으로 벡터 저장소(Collection) 생성 또는 기존 컬렉션 불러오기
collection = client.get_or_create_collection(COLLECTION_NAME)

# 참고: 기존 데이터가 있으면 삭제하고 새로 시작하는 코드는 주석 처리되었습니다.

collection.delete(ids=collection.get()['ids']) 

# 5. 데이터 준비: 청크, 메타데이터, ID 리스트 생성
# 인덱싱할 핵심 텍스트 데이터 (청크)
chunks = df['RAG_Chunk'].tolist()
# 검색 필터링에 사용될 메타데이터 (질병, 진료과, 생애주기 등)
metadata_list = df[['disease', 'department_meta', 'lifeCycle']].to_dict('records')
# 각 청크에 대한 고유 ID
ids_list = [f"chunk_{i:05d}" for i in range(len(chunks))] # ID 형식을 5자리 숫자로 변경하여 정렬 용이성 확보

print(f"\n--- 🚀 벡터 DB 인덱싱 시작 ---")
print(f"총 **{len(chunks)}**개의 지식 청크를 임베딩하고 **{COLLECTION_NAME}** 컬렉션에 저장합니다.")


# 6. 데이터 임베딩 및 배치 저장 (인덱싱)
# 데이터가 많을 경우 메모리 효율성을 위해 배치(Batch) 처리
batch_size = 32
for i in range(0, len(chunks), batch_size):
    # 현재 배치 데이터 슬라이싱
    batch_chunks = chunks[i:i + batch_size]
    batch_metadata = metadata_list[i:i + batch_size]
    batch_ids = ids_list[i:i + batch_size]

    # 임베딩 생성 (KoELECTRA 기반 SBERT 모델 사용)
    # [수정된 부분: NumPy 배열로 변환 후, Python 리스트로 최종 변환]
    batch_vectors = model.encode(batch_chunks, convert_to_numpy=True).tolist()

    # Chroma DB에 저장 (청크, 임베딩 벡터, 메타데이터, ID)
    collection.add(
        embeddings=batch_vectors, # 이미 리스트이므로 바로 전달
        documents=batch_chunks,
        metadatas=batch_metadata,
        ids=batch_ids
    )
    print(f"  > 배치 저장 완료: {i + len(batch_chunks)} / {len(chunks)} ({len(batch_chunks)}개 처리)")

print("\n--- ✅ 지식 기반(벡터 DB) 구축 완료 ---")
print(f"총 **{collection.count()}**개 항목 저장 완료.")
print(f"저장된 컬렉션 이름: **{COLLECTION_NAME}**")
print(f"DB 영구 저장 경로: **{DB_PATH}**")
print("이제 이 DB를 검색 증강 생성(RAG)에 활용할 수 있습니다.")