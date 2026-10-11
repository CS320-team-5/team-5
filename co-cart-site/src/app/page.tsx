function MyButton({ title }: { title: string }) {
  return (
    <button>{title}</button>
  );
}

export default function MyApp() {
  return (
    <div>
      <h1>{"This is a very basic website with only this line of text and a button that doesn't even look distinct from the text..."}</h1>
      <MyButton title="This is a button"/>
    </div>
  );
}