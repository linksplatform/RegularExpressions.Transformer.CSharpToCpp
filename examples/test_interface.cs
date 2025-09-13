interface ITest<T>
{
    void Method(T value);
}

class Implementation<T> : ITest<T>
{
    public void Method(T value) { }
}