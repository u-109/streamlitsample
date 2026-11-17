import json
import random
from datetime import date, timedelta
from pathlib import Path
import streamlit as st

st.set_page_config(page_title='Daily Words', page_icon='📘', layout='centered')
DATA_PATH = Path(__file__).with_name('words.json')
@st.cache_data
def load_words():
    with DATA_PATH.open(encoding='utf-8') as f:
        return json.load(f)
WORDS = load_words()
BY_WORD = {w['word']: w for w in WORDS}
LEVEL_NAMES = {1:'기본', 2:'핵심', 3:'심화'}

st.markdown('''<style>
.stApp {background:#f6f8ff;color:#263756}
.block-container {max-width:740px;padding-top:1.4rem}
h1,h2,h3 {color:#293f76}
div.stButton > button {border-radius:14px;border:1px solid #dce5f6;min-height:44px}
div.stButton > button[kind="primary"] {background:#506be9;color:white;border:0}
[data-testid="stMetric"] {background:white;padding:14px;border:1px solid #e1e8f5;border-radius:16px}
[data-testid="stVerticalBlockBorderWrapper"] {background:white;border-radius:18px}
</style>''', unsafe_allow_html=True)

DEFAULT = dict(placed=False,level=1,wrong={},status={},solved=0,correct=0,streak=[],page='홈',cards=[],card_i=0,flipped=False,quiz=[],quiz_i=0,quiz_log=[],quiz_checked=False,quiz_input='',placement=[],placement_i=0,placement_scores={1:0,2:0,3:0},placement_answered=False,retry_word=None,retry_checked=False)
for k,v in DEFAULT.items():
    if k not in st.session_state:
        st.session_state[k] = v.copy() if isinstance(v,(list,dict)) else v
S=st.session_state

def pool(level=None):
    return [w for w in WORDS if w['level']==(level or S.level)]
def sample(items,n):
    return random.sample(items,min(n,len(items)))
def touch_day():
    today=date.today().isoformat()
    if today not in S.streak:S.streak.append(today)
def streak_count():
    days=set(S.streak);d=date.today()
    if d.isoformat() not in days:d-=timedelta(days=1)
    n=0
    while d.isoformat() in days:n+=1;d-=timedelta(days=1)
    return n
def go(page):
    S.page=page
    S.retry_word=None
    st.rerun()
def mark_wrong(word,kind):
    info=S.wrong.get(word,{'count':0})
    S.wrong[word]={'count':info['count']+1,'kind':kind,'last':date.today().isoformat()}
def start_cards():
    S.cards=[w['word'] for w in sample(pool(),20)]
    S.card_i=0;S.flipped=False;go('단어 카드')
def start_quiz():
    S.quiz=[w['word'] for w in sample(pool(),10)]
    S.quiz_i=0;S.quiz_log=[];S.quiz_checked=False;S.quiz_input='';go('빈칸 퀴즈')
def start_placement():
    S.placement=sample([w['word'] for w in pool(1) if len(w['word'])>2],3)+sample([w['word'] for w in pool(2) if len(w['word'])>2],3)+sample([w['word'] for w in pool(3) if len(w['word'])>2],3)
    random.shuffle(S.placement)
    S.placement_i=0;S.placement_scores={1:0,2:0,3:0};S.placement_answered=False
    go('레벨 테스트')
def norm(s):return ' '.join(str(s).strip().casefold().split())
def quiz_data(w):
    return w.get('quiz') or {'s':'영어로 쓰세요: ___','tr':w['meaning'],'a':[w['word']],'note':'기본형 철자를 확인하세요.'}
def pronounce(word):
    import streamlit.components.v1 as components
    # Speech synthesis uses the learner's browser; voice availability varies by device.
    components.html('''<script>if(window.speechSynthesis){let u=new SpeechSynthesisUtterance('''+json.dumps(word)+''');u.lang='en-US';u.rate=.88;window.speechSynthesis.cancel();window.speechSynthesis.speak(u);}</script>''',height=0)

def header():
    st.title('📘 Daily Words')
    st.caption(f'Level {S.level} · {LEVEL_NAMES[S.level]} · {len(pool()):,}개 단어')
    tabs=st.columns(4)
    for col,label in zip(tabs,['홈','단어 카드','빈칸 퀴즈','복습']):
        if col.button(label,use_container_width=True,type='primary' if S.page==label else 'secondary',key='nav_'+label):go(label)
    st.divider()
header()

if S.page=='홈':
    st.subheader('오늘도 한 단어씩!')
    st.write('교육과정 어휘 3,000개를 레벨에 맞춰 학습해 보세요.')
    a,b,c=st.columns(3)
    a.metric('연속 학습',f'{streak_count()}일')
    b.metric('누적 정답률',f'{S.correct/S.solved:.0%}' if S.solved else '—')
    c.metric('오답 단어',len(S.wrong))
    st.subheader('학습 시작')
    c1,c2=st.columns(2)
    if c1.button('🃏 단어 카드 20개',use_container_width=True):start_cards()
    if c2.button('✏️ 빈칸 퀴즈 10문제',use_container_width=True):start_quiz()
    c3,c4=st.columns(2)
    if c3.button('🎯 레벨 테스트',use_container_width=True):start_placement()
    if c4.button('🔁 오답 복습',use_container_width=True):go('복습')
    new_level=st.selectbox('학습 레벨 직접 선택',[1,2,3],index=S.level-1,format_func=lambda x:f'Level {x} · {LEVEL_NAMES[x]}')
    if new_level!=S.level:
        S.level=new_level;S.cards=[];S.quiz=[];st.rerun()
    st.progress(sum(1 for w in pool() if S.status.get(w['word'])=='know')/max(1,len(pool())),text='현재 레벨 암기 완료 비율')
    st.caption('학습 기록은 현재 Streamlit 세션에 보관됩니다. 새 세션에서는 초기화될 수 있습니다.')

elif S.page=='레벨 테스트':
    st.subheader('🎯 레벨 진단')
    if S.placement_i>=len(S.placement):
        scores=S.placement_scores
        result=3 if scores[3]>=2 else 2 if scores[2]>=2 else 1
        st.success(f'진단 완료! 추천 레벨: Level {result} · {LEVEL_NAMES[result]}')
        st.write('레벨별 정답 수:',scores)
        if st.button('추천 레벨로 시작',type='primary'):
            S.level=result;S.placed=True;start_cards()
    else:
        w=BY_WORD[S.placement[S.placement_i]]
        st.progress(S.placement_i/len(S.placement),text=f'{S.placement_i+1} / {len(S.placement)}')
        st.markdown(f'### {w["word"]}')
        st.caption('알맞은 한국어 뜻을 고르세요.')
        key=f'placement_options_{S.placement_i}'
        if key not in S:
            other=[x['meaning'] for x in pool(w['level']) if x['word']!=w['word'] and x['meaning']!=w['meaning']]
            S[key]=sample(list(dict.fromkeys(other)),3)+[w['meaning']]
            random.shuffle(S[key])
        for i,option in enumerate(S[key]):
            if st.button(option,key=f'place_{S.placement_i}_{i}',use_container_width=True,disabled=S.placement_answered):
                S.placement_answered=True
                if option==w['meaning']:S.placement_scores[w['level']]+=1
                st.rerun()
        if S.placement_answered:
            st.info(f'정답: {w["meaning"]}')
            if st.button('다음 문제',type='primary'):
                S.placement_i+=1;S.placement_answered=False;st.rerun()

elif S.page=='단어 카드':
    if not S.cards:
        if st.button('20개 단어 학습 시작',type='primary'):start_cards()
    elif S.card_i>=len(S.cards):
        st.success('20개 단어 학습 완료!')
        known=sum(S.status.get(w)=='know' for w in S.cards)
        st.metric('알고 있는 단어',f'{known}/{len(S.cards)}')
        if st.button('새 카드 세트',type='primary'):start_cards()
    else:
        w=BY_WORD[S.cards[S.card_i]]
        st.progress(S.card_i/len(S.cards),text=f'{S.card_i+1} / {len(S.cards)}')
        with st.container(border=True):
            if not S.flipped:
                st.caption(f'Level {w["level"]} · {w.get("pos","")}')
                st.markdown(f'<h1 style="text-align:center;padding:40px 0;color:#293b60">{w["word"]}</h1>',unsafe_allow_html=True)
                st.caption('뜻을 확인하려면 아래 버튼을 누르세요.')
            else:
                st.markdown(f'### {w["word"]}')
                st.markdown(f'## {w["meaning"]}')
                if w.get('variation'):st.caption('변형: '+', '.join(w['variation']))
                if w.get('family'):st.caption('어족: '+', '.join(map(str,w['family'])))
                st.write('**예문**',w.get('ex','—'))
            c1,c2=st.columns(2)
            if c1.button('↩️ 카드 뒤집기',use_container_width=True):S.flipped=not S.flipped;st.rerun()
            if c2.button('🔊 발음 듣기',use_container_width=True):pronounce(w['word'])
        c1,c2=st.columns(2)
        if c1.button('❌ 아직 몰라요',use_container_width=True):
            S.status[w['word']]='dont';mark_wrong(w['word'],'card');touch_day();S.card_i+=1;S.flipped=False;st.rerun()
        if c2.button('✅ 알고 있어요',use_container_width=True,type='primary'):
            S.status[w['word']]='know';touch_day();S.card_i+=1;S.flipped=False;st.rerun()
        if st.button('← 이전 카드'):
            S.card_i=max(0,S.card_i-1);S.flipped=False;st.rerun()

elif S.page=='빈칸 퀴즈':
    if not S.quiz:
        st.subheader('오늘의 10문제')
        st.write('예문과 한국어 해석을 보고 빈칸에 들어갈 영어 단어를 입력하세요.')
        if st.button('퀴즈 시작',type='primary'):start_quiz()
    elif S.quiz_i>=len(S.quiz):
        score=sum(x['correct'] for x in S.quiz_log)
        st.success(f'퀴즈 완료! {score}/{len(S.quiz)}점')
        for row in S.quiz_log:
            with st.expander(('✅ ' if row['correct'] else '❌ ')+row['word']):
                st.write('입력:',row['answer'],'| 정답:',row['expected'])
        if st.button('새 퀴즈',type='primary'):start_quiz()
    else:
        w=BY_WORD[S.quiz[S.quiz_i]];q=quiz_data(w)
        st.progress(S.quiz_i/len(S.quiz),text=f'{S.quiz_i+1} / {len(S.quiz)}')
        with st.container(border=True):
            st.markdown('### '+q.get('s','___'))
            st.write(q.get('tr',''))
            if not S.quiz_checked:
                with st.form('quiz_form',clear_on_submit=False):
                    answer=st.text_input('빈칸 정답',key=f'answer_{S.quiz_i}',placeholder='영어 단어 입력')
                    submitted=st.form_submit_button('정답 확인',type='primary')
                if submitted and answer.strip():
                    ok=norm(answer) in [norm(a) for a in q.get('a',[w['word']])]
                    S.quiz_log.append(dict(word=w['word'],answer=answer,expected=', '.join(q.get('a',[w['word']])),correct=ok))
                    S.solved+=1;S.correct+=int(ok)
                    if not ok:mark_wrong(w['word'],'blank')
                    touch_day();S.quiz_checked=True;st.rerun()
            else:
                last=S.quiz_log[-1]
                if last['correct']:st.success('Great job! 정답입니다.')
                else:st.error('Try again next time! 정답: '+last['expected'])
                st.info(q.get('note','기본형 철자를 확인하세요.'))
                if st.button('다음 문제 →',type='primary'):
                    S.quiz_i+=1;S.quiz_checked=False;st.rerun()

elif S.page=='복습':
    st.subheader('🔁 나만의 오답 복습')
    a,b,c=st.columns(3)
    a.metric('오답 단어',len(S.wrong));b.metric('누적 정답',S.correct);c.metric('풀이 수',S.solved)
    if S.retry_word:
        w=BY_WORD[S.retry_word]
        st.markdown(f'### {w["word"]}')
        st.write('뜻:',w['meaning'])
        if not S.retry_checked:
            with st.form('retry_form'):
                value=st.text_input('영어 단어를 다시 입력하세요',key='retry_answer')
                submit=st.form_submit_button('채점',type='primary')
            if submit and value.strip():
                ok=norm(value)==norm(w['word'])
                S.solved+=1;S.correct+=int(ok);touch_day()
                if ok:S.wrong.pop(w['word'],None)
                else:mark_wrong(w['word'],'retry')
                S.retry_checked=True;S.retry_ok=ok;st.rerun()
        else:
            if S.retry_ok:st.success('정답! 오답 목록에서 제거했어요.')
            else:st.error(f'정답은 {w["word"]}입니다.')
        if st.button('← 복습 목록으로'):
            S.retry_word=None;S.retry_checked=False;st.rerun()
    elif not S.wrong:
        st.info('아직 복습할 단어가 없어요. 카드 학습이나 퀴즈를 시작해 보세요!')
    else:
        level_filter=st.selectbox('레벨 필터',['전체',1,2,3],format_func=lambda x:'전체' if x=='전체' else f'Level {x}')
        keys=[word for word in S.wrong if word in BY_WORD and (level_filter=='전체' or BY_WORD[word]['level']==level_filter)]
        for word in sorted(keys,key=lambda x:-S.wrong[x]['count']):
            w=BY_WORD[word]
            with st.container(border=True):
                c1,c2=st.columns([4,1])
                c1.markdown(f'**{word}** · {w["meaning"]}')
                c1.caption(f'Level {w["level"]} · 틀린 횟수 {S.wrong[word]["count"]}회')
                if c2.button('재시험',key='retry_'+word):
                    S.retry_word=word;S.retry_checked=False;st.rerun()

with st.sidebar:
    st.subheader('학습 기록 백업')
    record={k:S[k] for k in ['placed','level','wrong','status','solved','correct','streak']}
    st.download_button('JSON으로 내보내기',json.dumps(record,ensure_ascii=False,indent=2),file_name='daily_words_progress.json',mime='application/json')
    uploaded=st.file_uploader('기존 학습 기록 불러오기',type='json')
    if uploaded and st.button('기록 적용'):
        try:
            data=json.load(uploaded)
            for key in record:
                if key in data and isinstance(data[key],type(DEFAULT[key])):S[key]=data[key]
            st.success('기록을 불러왔습니다.');st.rerun()
        except (ValueError,TypeError) as e:st.error(f'파일을 확인해 주세요: {e}')
