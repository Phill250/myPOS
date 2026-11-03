// Shapes returned by the FastAPI backend. Keep in sync with backend/schemas.

export type Role = "customer" | "staff" | "super_admin";

export type PaymentMethod =
  | "cash"
  | "mtn_momo"
  | "airtel_money"
  | "card"
  | "bank_transfer";

export interface Customer {
  customer_id: number;
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string | null;
  library_member: boolean;
  user_id: number | null;
}

export interface User {
  user_id: number;
  username: string;
  role: Role;
  is_active: boolean;
}

export interface Me extends User {
  customer_profile: Customer | null;
}

export interface Book {
  book_id: number;
  title: string;
  author: string;
  isbn: string | null;
  sale_price: string | number; // Decimal arrives as a string
  category_id: number;
  supplier_id: number;
  retail_stock: number;
  library_stock: number;
}

export interface Category {
  category_id: number;
  category_name: string;
  description: string | null;
}

export interface Supplier {
  supplier_id: number;
  company_name: string;
  phone_number: string;
}

export interface PaymentOut {
  payment_id: number;
  amount: number;
  payment_method: string;
  transaction_type: "sale" | "rental_fee" | "late_fee" | string;
  paid_at: string | null;
}

export interface SaleSummary {
  sale_id: number;
  sale_timestamp: string;
  total_amount: number;
  customer_id: number | null;
  customer_name: string | null;
  cashier: string | null;
  item_count: number;
  payment_method: string | null;
  receipt_number: string | null;
}

export interface SaleLine {
  sale_item_id: number;
  book_id: number;
  title: string;
  author: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface SaleDetail extends SaleSummary {
  items: SaleLine[];
  payments: PaymentOut[];
}

export type RentalStatus = "active" | "overdue" | "returned";

export interface RentalSummary {
  rental_id: number;
  rental_timestamp: string;
  expected_return: string;
  actual_return: string | null;
  status: RentalStatus;
  days_overdue: number;
  customer_id: number;
  customer_name: string | null;
  customer_phone: string | null;
  staff: string | null;
  books: { rental_item_id: number; book_id: number; title: string; author: string }[];
  receipt_number: string | null;
}

export interface RentalDetail extends RentalSummary {
  payments: PaymentOut[];
  late_fee_per_day: number;
  suggested_late_fee: number;
}

export interface Dashboard {
  today: {
    sales_count: number;
    sales_revenue: number;
    items_sold: number;
    library_income: number;
    loans_out: number;
    returns: number;
  };
  last_7_days: { date: string; sales_count: number; revenue: number }[];
  payment_methods_today: { method: string; amount: number }[];
  active_loans: number;
  overdue_loans: number;
  low_stock: {
    book_id: number;
    title: string;
    author: string;
    retail_stock: number;
    library_stock: number;
  }[];
  top_books_30_days: { book_id: number; title: string; quantity: number; revenue: number }[];
  total_titles: number;
  total_customers: number;
  library_members: number;
}
