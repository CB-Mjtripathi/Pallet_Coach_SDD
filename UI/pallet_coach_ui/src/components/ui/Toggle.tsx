interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  id?: string;
}

export function Toggle({ checked, onChange, label = "Enabled", id }: ToggleProps): JSX.Element {
  return (
    <label className="toggle-wrap" htmlFor={id}>
      <input
        id={id}
        className="toggle-input"
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="toggle-track" aria-hidden="true">
        <span className="toggle-thumb" />
      </span>
      <span className="toggle-label">{label}</span>
    </label>
  );
}
