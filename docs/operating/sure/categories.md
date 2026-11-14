# Category Mapping (Banksalad → Sure)

Sure uses English categories with two levels. Banksalad `major > minor` maps as below; a minor of `미분류` goes to the parent only.

## Expenses

| Banksalad | Sure parent | Children |
| --- | --- | --- |
| 교통 | Transportation | 대중교통 Public Transit, 택시 Taxi, 철도 Rail |
| 생활 | Living | 편의점 Convenience Store, 마트 Supermarket, 생필품 Household Supplies, 가구/가전 Furniture & Appliances, 생활서비스 Household Services, 세탁 Laundry |
| 식비 | Food | 배달 Delivery, 패스트푸드 Fast Food, 한식 Korean Food, 식재료 Groceries, 양식 Western Food, 치킨 Chicken, 고기 Meat & BBQ, 일식 Japanese Food, 아시아음식 Asian Food, 중식 Chinese Food, 피자 Pizza |
| 카페/간식 | Cafe & Snacks | 커피/음료 Coffee & Drinks, 베이커리 Bakery, 아이스크림/빙수 Ice Cream, 도넛/핫도그 Donuts & Hot Dogs, 디저트/떡 Desserts, 기타간식 Other Snacks |
| 온라인쇼핑 | Online Shopping | 인터넷쇼핑 Online Stores, 서비스구독 Subscriptions, 앱스토어 App Store, 결제/충전 Top-ups |
| 의료/건강 | Healthcare | 종합병원 General Hospital, 정형외과 Orthopedics, 약국 Pharmacy, 치과 Dental, 산부인과 Obstetrics & Gynecology, 내과/가정의학 Internal Medicine, 운동 Fitness, 건강용품 Health Products, 보조식품 Supplements, 한의원 Korean Medicine, 기타병원 Other Clinics, 안과 Ophthalmology, 피부과 Dermatology |
| 금융 | Finance | 보험 Insurance, 은행 Bank Fees, 카드 Card Fees, 세금/과태료 Taxes & Fines, 증권/투자 Brokerage Fees, 이자/대출 Interest, (loan principal) Loan Repayment |
| 교육/학습 | Education | 학교 School, 학원/강의 Courses, 학습교재 Study Materials, 시험료 Exam Fees |
| 문화/여가 | Entertainment | 게임 Games, 취미/체험 Hobbies, 도서 Books, 스포츠 Sports, 영화 Movies, 공연 Performances, 음악 Music, 전시/관람 Exhibitions |
| 주거/통신 | Housing & Utilities | 휴대폰 Mobile Phone, 가스비 Gas Bill, 전기세 Electricity, 관리비 Maintenance Fees, 인터넷 Internet |
| 뷰티/미용 | Beauty | 헤어샵 Hair Salon, 화장품 Cosmetics, 미용용품 Beauty Supplies |
| 패션/쇼핑 | Fashion | 패션 Clothing, 백화점 Department Store, 신발 Shoes, 스포츠의류 Sportswear |
| 경조/선물 | Gifts & Donations | 선물 Gifts, 기부/헌금 Donations |
| 여행/숙박 | Travel | 여행 Trips, 숙박비 Lodging |
| 자녀/육아 | Childcare | 육아용품 Baby Supplies, 돌봄비 Care Services, 놀이/체험 Kids Activities |
| 반려동물 | Pets | 펫용품 Pet Supplies, 동물병원 Veterinary |
| 자동차 | Car | 주유 Fuel, 정비/수리 Car Maintenance |
| 술/유흥 | Alcohol & Bars | 맥주/호프 Pubs |

| (none) | Family | Family events, such as wedding photos. Sure only, no Banksalad source. |

- 뷰티/미용 > 피부과 also goes to Healthcare > Dermatology.
- Category names are unique per family, so children that would repeat a parent were renamed: 여행 → Trips, 돌봄비 → Care Services.

## Income

| Banksalad | Sure |
| --- | --- |
| 급여 | Salary |
| 금융수입 | Financial Income |
| 기타수입 | Other Income |

- Pay from an employer is Salary even when the export types it as a transfer.
- Payouts of contributions withheld from pay (mutual-aid funds and similar) are also Salary.

## Transfer Types with Exceptions

Banksalad `이체` rows become Sure transfers (see transfers-and-loans.md), except:

| Banksalad transfer type | Sure |
| --- | --- |
| 보험 | Expense Finance > Insurance |
| 카드대금 to a charity | Expense Gifts & Donations > Donations |
| 카드대금 to a shop | Expense in the matching category |

## Earlier Generic Categories

Older Sure transactions that used Sure's default categories map as follows.

| Earlier | Now |
| --- | --- |
| Food & Drink | Food |
| Groceries | Food > Groceries |
| Subscriptions | Online Shopping > Subscriptions |
| Personal Care | Beauty |
| Shopping | Fashion |
| Fees | Finance > Bank Fees |
| Loan and Card | Finance > Interest |
| Income | Other Income |

Transportation, Entertainment, Gifts & Donations, Education and Healthcare keep their names.
