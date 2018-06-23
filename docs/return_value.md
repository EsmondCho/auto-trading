# 1. 초기입력 & 허매수_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- init_price : 초기금액
- celery_checked : 샐러리 체크

# 2. altcoin 선택_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- bid_alt_code : 코인 이름
- bid_alt_amt : 코인 수량
- thumb_alt_price : bithumb 해당 alt 가격 (krw)
- celery_checked : 샐러리 체크

# 3. bid 신청_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- bid_order_id : 실제 order_id (bithumb)
- bid_alt_code : 코인 이름
- bid_alt_amt : 코인 수량
- thumb_alt_price : bithumb 해당 alt 가격 (krw)
- thumb_btc_price : bithumb 비트 가격(krw)
- thumb_alt_value : bithumb 해당 alt 비트 가격 (btc)
- trex_alt_value : bittrex 해당 alt 가격 (btc)
- celery_checked : 샐러리 체크

# 4. bid 완료_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- celery_checked : 샐러리 체크

# 5. withdrawal 신청_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- thumb_out_alt_code : 출금 alt 이름
- thumb_out_alt_amt : 출금 alt 수량
- celery_checked : 샐러리 체크

# 6. withdrawal 완료_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- celery_checked : 샐러리 체크

# 7. deposit 완료_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- trex_in_alt_code : 입금 alt 이름
- trex_in_alt_amt : 입금 alt 수량
- celery_checked : 샐러리 체크

# 8. ask 신청_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- ask_alt_code : 코인 이름
- ask_alt_amt : 코인 수량
- ask_order_id : 실제 order_id (bittrex)
- thumb_btc_price : bithumb 비트 가격(krw)
- thumb_alt_price : bithumb 해당 alt 가격 (krw)
- thumb_alt_value : bithumb 해당 alt 비트 가격 (btc)
- trex_alt_value : bittrex 해당 alt 가격 (btc)
- celery_checked : 샐러리 체크

# 9. ask 완료_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- celery_checked : 샐러리 체크

# 10. altcoin' 선택_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- bid_alt_code : 코인 이름
- bid_alt_amt : 코인 수량
- trex_alt_value : bittrex 해당 alt 가격 (btc)
- celery_checked : 샐러리 체크

# 11. bid 신청_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- bid_order_id : 실제 order_id (bittrex)
- bid_alt_code : 코인 이름
- bid_alt_amt : 코인 수량
- thumb_btc_price : bithumb 비트 가격(krw)
- thumb_alt_price : bithumb 해당 alt 가격 (krw)
- thumb_alt_value : bithumb 해당 alt 비트 가격 (btc)
- trex_alt_value : bittrex 해당 alt 가격 (btc)
- celery_checked : 샐러리 체크

# 12. bid 완료_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- celery_checked : 샐러리 체크

# 13. withdrawal 신청_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- trex_out_alt_code : 출금 alt 이름
- trex_out_alt_amt : 출금 alt 수량
- celery_checked : 샐러리 체크

# 14. withdrawal 완료_bittrex
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- celery_checked : 샐러리 체크

# 16. deposit 완료_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- thumb_in_alt_code : 입금 alt 이름
- thumb_in_alt_amt : 입금 alt 수량
- celery_checked : 샐러리 체크

# 17. ask 신청_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- ask_alt_code : 코인 이름
- ask_alt_amt : 코인 수량
- ask_order_id : 실제 order_id (bithumb)
- thumb_btc_price : bithumb 비트 가격(krw)
- thumb_alt_price : bithumb 해당 alt 가격 (krw)
- thumb_alt_value : bithumb 해당 alt 비트 가격 (btc)
- trex_alt_value : bittrex 해당 alt 가격 (btc)
- celery_checked : 샐러리 체크

# 18. ask 완료_bithumb
- tube_id : 허매수 order_id
- tube_step : tube 단계
- executed_time : 실행시간
- celery_checked : 샐러리 체크

# 19. (모든 단계 종료) 이후
1. django는 해당 tube process의 종합 정보를 redis에서 read
2. 종합 정보를 정리
3. mysql에 write
4. redis 해당 tube process 삭제
