import { fireEvent, render, screen, within } from '@testing-library/react';
import App from './App';

describe('Vector design workspace', () => {
  it('renders the required decision tree fields and specialised free-text capacity', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Cloning & Expression Vector Design Toolkit' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /01 Objective/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /07 Biosafety tier/ })).toBeInTheDocument();

    const specialisedNotes = screen.getByLabelText('Other / specialised - describe your requirement');
    expect(specialisedNotes).toHaveAttribute('maxLength', '2000');
  });

  it('shows GMExpression branding and copyright details', () => {
    render(<App />);

    expect(screen.getByRole('link', { name: 'GMExpression shop' })).toHaveAttribute(
      'href',
      'https://shop.gmexpression.com/'
    );
    expect(screen.getByText(/2026 GMExpression/)).toBeInTheDocument();
    expect(screen.getByText(/For Research Use Only/)).toBeInTheDocument();
  });

  it('exposes the First-Edition user-guide PDF from the upper-right nav', () => {
    render(<App />);

    const guideLink = screen.getByRole('link', {
      name: /First Edition user guide/i
    });
    expect(guideLink).toHaveAttribute(
      'href',
      '/Cloning_Expression_Vector_Design_Toolkit_First_Edition.pdf'
    );
    expect(guideLink).toHaveAttribute('target', '_blank');
    expect(guideLink).toHaveAttribute('rel', 'noreferrer');
    expect(guideLink).toHaveAttribute('title', 'User Guide — First Edition (PDF)');
  });

  it('renders the workflow-grade wet-lab planning surfaces', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'EV-2407' })).toBeInTheDocument();
    expect(screen.getByText('Blocked by review gate')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Workflow stages' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /06 Biosafety review/ })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Import and selection' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Import sequence' })).toBeInTheDocument();
  });

  it('renders construct architecture, compatibility, and gated export actions', () => {
    render(<App />);

    expect(screen.getByText('Construct architecture')).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: 'cargo ORF' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Compatibility matrix' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cargo \/ tag/ })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Action and export' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Validate design/ })).toBeEnabled();
    expect(screen.getByRole('button', { name: /Final GenBank\/SBOL\/FASTA export/ })).toBeDisabled();
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
