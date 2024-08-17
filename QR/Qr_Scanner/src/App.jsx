import { useEffect } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

function App() {
  useEffect(() => {
    function onScanSuccess(qrCodeMessage) {
      document.getElementById('qr-result').innerText = `QR Code Result: ${qrCodeMessage}`;
    }

    function onScanError(errorMessage) {
      console.warn(`QR scan error: ${errorMessage}`);
    }

    const html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(onScanSuccess, onScanError);

    return () => {
      html5QrcodeScanner.clear();  
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-500 flex flex-col items-center justify-center">
      <h1 className="text-2xl text-center text-amber-300 font-bold mb-4">QR Code Scanner</h1>
      <div id="qr-reader" className="w-72 mx-auto mb-4 border border-gray-300 p-4"></div>
      <div id="qr-result" className="text-center text-amber-50 ">Result will be shown here</div>
    </div>
  );
}
export default App;