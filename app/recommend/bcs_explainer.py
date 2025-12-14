def explain_bcs(bcs: int) -> str:
    if bcs <= 3:
        return f"현재 BCS {bcs}로 저체중 상태이므로 고영양 사료를 추천합니다."
    elif 4 <= bcs <= 5:
        return f"현재 BCS {bcs}로 정상 체중 상태이므로 유지용 사료를 추천합니다."
    elif 6 <= bcs <= 7:
        return f"현재 BCS {bcs}로 약간 과체중 상태이므로 체중 관리 사료를 추천합니다."
    else:
        return f"현재 BCS {bcs}로 과체중 상태이므로 다이어트 사료를 추천합니다."
