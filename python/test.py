# -*- coding: utf-8 -*-
from unittest import main, TestCase

from cs2cpp import CSharpToCpp


class CSharpToCppTest(TestCase):
    translator = CSharpToCpp()

    def test_translate_hello_world(self):
        print(
            self.translator.translate(
                ('''
                 using System;
                 // This is hello world program.
                 class Program
                 {
                     public static void Main(string[] args)
                     {
                         var myFirstString = "ban";
                         char*[] args = {"1", "2"};
                         Console.WriteLine("Hello, world!");
                     }
                 }''')))

    def test_some(self):
        print(
            self.translator.translate(
                ('''
                 namespace Platform.Interfaces
                 {
                     /// <summary>
                     /// <para>Defines a factory that produces instances of a specific type.</para>
                     /// <para>Определяет фабрику, которая производит экземпляры определенного типа.</para>
                     /// </summary>
                     /// <typeparam name="TProduct"><para>Type of produced instances.</para><para>Тип производимых экземпляров.</para></typeparam>
                     public interface IFactory<out TProduct>
                     {
                         /// <summary>
                         /// <para>Creates an instance of TProduct type.</para>
                         /// <para>Создает экземпляр типа TProduct.</para>
                         /// </summary>
                         /// <returns><para>The instance of TProduct type.</para><para>Экземпляр типа TProduct.</para></returns>
                         TProduct Create();
                     }
                 }''')))

if __name__ == '__main__':
    main(verbosity=2)
