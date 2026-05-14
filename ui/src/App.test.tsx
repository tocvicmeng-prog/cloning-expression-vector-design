import { fireEvent, render, screen, within } from '@testing-library/react';
import App from './App';

describe('Vector design workspace', () => {
  it('renders the required decision tree fields and specialised free-text capacity', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Vector Design Workspace' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /01 Objective/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /07 Biosafety tier/ })).toBeInTheDocument();

    const specialisedNotes = screen.getByLabelText('Other / specialised - describe your requirement');
    expect(specialisedNotes).toHaveAttribute('maxLength', '2000');
  });

  it('exposes only acknowledge, decline, and escalate as advisory decision paths', () => {
    render(<App />);

    const advisoryDialog = screen.getByTestId('advisory-actions');
    expect(within(advisoryDialog).getByRole('button', { name: /Acknowledge/ })).toBeInTheDocument();
    expect(within(advisoryDialog).getByRole('button', { name: /Decline/ })).toBeInTheDocument();
    expect(within(advisoryDialog).getByRole('button', { name: /Escalate/ })).toBeInTheDocument();
    expect(within(advisoryDialog).queryByRole('button', { name: /dismiss|close|cancel/i })).not.toBeInTheDocument();
  });

  it('requires evidence before recording an acknowledgement or escalation', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Acknowledge/ }));
    expect(screen.getByRole('button', { name: 'Record decision' })).toBeDisabled();

    fireEvent.change(screen.getByLabelText('Justification record'), {
      target: { value: 'Reviewer confirmed documented institutional controls.' }
    });
    expect(screen.getByRole('button', { name: 'Record decision' })).toBeEnabled();

    fireEvent.click(screen.getByRole('button', { name: /Escalate/ }));
    expect(screen.getByRole('button', { name: 'Record decision' })).toBeDisabled();

    fireEvent.change(screen.getByLabelText('Institutional approval ID'), {
      target: { value: 'IRB-7782' }
    });
    expect(screen.getByRole('button', { name: 'Record decision' })).toBeEnabled();
  });

  it('links validation findings back to wizard modules', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Biosafety tier Institutional review acknowledgement/ }));

    const biosafetySelect = screen.getByRole('combobox', { name: /Biosafety tier/ });
    expect(biosafetySelect).toHaveValue('Standard institutional review');
  });

  it('renders circular and linear vector maps with translation frame highlights', () => {
    render(<App />);

    expect(screen.getByRole('img', { name: 'Circular plasmid map' })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Scrollable feature map' })).toBeInTheDocument();
    expect(screen.getByText('Frame +1')).toBeInTheDocument();
    expect(screen.getByText('ATG')).toHaveClass('start');
    expect(screen.getByText('TAA')).toHaveClass('stop');
  });
});
