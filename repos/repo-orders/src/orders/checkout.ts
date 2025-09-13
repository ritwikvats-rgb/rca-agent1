// Bug: no timeout guard. Will violate Checkout PRD (5s SLA).
export class CheckoutTimeoutError extends Error {}

async function fakePaymentCall(ms: number): Promise<string> { 
  return new Promise(res => setTimeout(res, ms)); 
}

export async function checkout(amount: number): Promise<string> {
  const started = Date.now();
  await fakePaymentCall(6000); // simulate a slow gateway (6s)
  if (Date.now() - started > 5000) {
    throw new CheckoutTimeoutError('payment gateway exceeded 5s');
  }
  return 'OK';
}
