export interface BaseProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ButtonProps extends BaseProps {
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
}

export interface InputProps extends BaseProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  type?: 'text' | 'textarea';
  rows?: number;
} 