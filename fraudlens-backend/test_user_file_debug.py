import asyncio
import io
import pandas as pd
from fastapi import UploadFile
from app.database import SessionLocal
from app.models.user import User
from app.models.investigation import Investigation
from app.services.transaction_service import TransactionService

async def main():
    db = SessionLocal()
    user = db.query(User).first()
    inv = Investigation(user_id=user.id, type='UPI', status='PROCESSING', target_entity='test.csv')
    db.add(inv)
    db.commit()
    db.refresh(inv)
    
    with open('temp_uploads/4cabdc3ec72b44e7a16229c3eafaaad0.csv', 'rb') as f:
        content = f.read()
    
    uf = UploadFile(filename='4cabdc3ec72b44e7a16229c3eafaaad0.csv', file=io.BytesIO(content))
    res = await TransactionService.process_transaction_file(db, user.id, uf, inv.id)
    print('Total txns:', res['total_transactions'])
    print('Baseline mean:', res['user_historical_mean'])
    print('Risk score:', res['risk_score'], res['risk_level'])
    for t in res['transactions'][:5]:
        print(t['transaction_id'], t['receiver_id'], t['amount'], t['baseline_mean'], t['amount_ratio'], t['xgboost_score'], t['anomaly_score'], t['is_anomalous'])

if __name__ == '__main__':
    asyncio.run(main())
