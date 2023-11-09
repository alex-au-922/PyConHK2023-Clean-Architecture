// .loader-container {
//     width: 100vw;
//     height: 100vh;
//     display: flex;
//     justify-content: center;
//     align-items: center;
//     position: fixed;
//     background: rgba(0, 0, 0, 0.834);
//     z-index: 200000 !important;
// }

// .spinner {
//     width: 64px;
//     height: 64px;
//     border: 8px solid;
//     border-color: #3d5af1 transparent #3d5af1 transparent;
//     border-radius: 50%;
//     animation: spin-anim 1.2s linear infinite;
// }

// @keyframes spin-anim {
//     0% {
//         transform: rotate(0deg);
//     }
//     100% {
//         transform: rotate(360deg);
//     }
// }

// import "./App.css";

const FullScreenSpinner = () => {
  return (
    <div className="w-screen h-screen flex justify-center items-center fixed z-[10000] bg-black/[.834]">
      <div className="w-28 h-28 border-solid border-4 rounded-full animate-spin"></div>
    </div>
  );
};

export default FullScreenSpinner;
