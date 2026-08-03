**A Point of Sale & Library Management API Engine**

A robust, enterprise-grade RESTful API built with FastAPI, SQLAlchemy, and PostgreSQL that implements a comprehensive Point of Sale (POS) book retail system alongside an automated library book rental and tracking facility.
 Architectural Pillars

 Clean Architecture Pattern: Strict segregation of project boundaries spanning Models, Schemas, Repositories, Services and Routers to maximize testability and maintenance decoupling.
 
** Automated Inventory Lifecycle Engine**: Fully integrated, transactional service logic that maintains stock counts safely without race 
 conditions:
 -Submitting a retail transaction line item automatically validates title availability and decrements the book's retail_stock.
 -Submitting a library rental checkout dynamically validates and decrements the book's shelf-allocated library_stock.
 -Logging an actual_return timestamp via a PUT request on library rentals instantly triggers a symmetric relationship traversal to increment stock counts back onto shelf balances.
 
 **Data Integrity & Relational Guardrails: **Active foreign key database validations mapping categories, suppliers, items, users, and customers to eliminate orphan rows, outputting clean HTTP exceptions rather than server-crashing tracebacks.
