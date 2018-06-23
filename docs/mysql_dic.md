# settings
- tube_id : 허매수 order_id  
- set_price : 1단계 init_price  
---

# exchanges
- ex1_name : 'bithumb'
- ex2_name : 'bittrex'
- ex3_name : 'bithumb'  
---

# time
0. init time
    - set_time : 1단계 tube init 시간
    - end_time : 전체 closing 시간 (process 완료시)

1. source (bithumb)
    - ex1_bid_start_time : 2단계 bid 시작 시간
    - ex1_bid_end_time : 4단계 bid 완료 시간
    - ex1_with_start_time : 5단계 withdrawal 실행시간
    - ex1_with_end_time : 6단계 withdrawal 완료시간

2. layover (bittrex)
    - ex2_depo_start_time : 7단계 deposit 완료시간
    - ex2_ask_start_time : 8단계 ask 실행 시간
    - ex2_ask_end_time : 9단계 ask 완료 시간
    - ex2_bid_start_time : 11단계 bid 시작 시간
    - ex2_bid_end_time : 12단계 bid 완료 시간
    - ex2_with_start_time : 13단계 withdrawal 실행시간
    - ex2_with_end_time : 14단계 withdrawal 완료시간

3. destination (bithumb)
    - ex3_depo_start_time : 15단계 deposit 완료시간
    - ex3_ask_start_time : 17단계 ask 실행 시간
    - ex3_ask_end_time : 18단계 ask 완료 시간
---


# bid/ask price & value
1. source (bithumb)
    - ex1_bid_alt_price : 3단계 thumb_alt_price
    - ex1_bid_bit_price : 3단계 thumb_btc_price  
    - ex1_bid_alt_value : 3단계 thumb_alt_value  
    - ex2_dest_alt_value : 3단계 trex_alt_value

2. layover (bittrex)
    - ex1_src_bit_price : 8단계 thumb_btc_price
    - ex1_src_alt_price : 8단계 thumb_alt_price
    - ex1_src_alt_value : 8단계 thumb_alt_value
    - ex2_ask_alt_value : 8단계 trex_alt_value
    - ex3_dest_bit_price : 11단계 thumb_btc_price  
    - ex3_dest_alt_price : 11단계 thumb_alt_price
    - ex3_dest_alt_value : 11단계 thumb_alt_value  
    - ex2_bid_alt_value : 11단계 trex_alt_value

3. destination (bittrex)
    - ex3_ask_bit_price : 17단계 thumb_btc_price  
    - ex3_ask_alt_price : 17단계 thumb_alt_price  
    - ex3_ask_alt_value : 17단계 thumb_alt_value  
    - ex2_src_alt_value : 17단계 trex_alt_value  

---


# order_manage
1. source (bithumb)
    - ex1_bid_order_id : 3단계 bid_order_id
    - ex1_coin_code : 3단계 bid_alt_code
    - ex1_coin_amt : 3단계 bid_alt_amt

2. layover (bittrex)
    - ex2_ask_order_id : 8단계 ask_order_id
    - ex2_coin_code : 7단계 trex_in_alt_code (*deposit coin code*)
    - ex2_coin_amt : 7단계 trex_in_alt_amt (*deposit coin amt*)
    - ex2_bid_order_id : 11단계 bid_order_id
    - ex2_coin_code : 10단계 bid_alt_code
    - ex2_coin_amt : 10단계 bid_alt_amt

3. destination (bithumb)
    - ex3_ask_order_id : 17단계 ask order_id
    - ex3_coin_code : 14단계 thumb_in_alt_code (*deposit coin code*)  
    - ex3_coin_amt : 14단계 thumb_in_alt_amt (*deposit coin amt*)  

##### 수정사항 : deposit coin amout 같은 경우 실제 ask의 amount와 달라질 수 있음